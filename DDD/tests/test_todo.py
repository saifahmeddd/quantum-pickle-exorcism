"""Behavior and dependency tests for the authenticated DDD request path."""

import ast
import unittest
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from application.dtos.task_dto import CreateTaskDTO
from application.exceptions.task_not_found import TaskNotFound
from application.interfaces.authentication import AuthenticatedUser
from application.services.task_service import TaskService
from domain.domain_services.task_ordering import TaskOrdering
from domain.exceptions.task_errors import InvalidTask
from domain.value_objects.task_id import TaskId
from domain.value_objects.task_title import TaskTitle
from domain.value_objects.user_id import UserId
from infrastructure.providers.system_runtime import UUIDGenerator
from infrastructure.repositories.firestore_task_repository import (
    TASK_DOCUMENT_FIELDS,
    FirestoreTaskRepository,
)
from presentation.controllers.task_controller import TaskController
from presentation.routes.task_routes import TaskRoutes
from presentation.validators.task_validator import InvalidRequest
from tests.fake_firestore import FakeFirestoreClient


class FixedClock:
    """Return a stable timestamp so output assertions are deterministic."""

    def now(self):
        return datetime(2026, 1, 1, tzinfo=timezone.utc)


class RecordingPublisher:
    """Record published events without calling an external message system."""

    def __init__(self):
        self.events = []

    def publish(self, event):
        self.events.append(event)


class TodoTests(unittest.TestCase):
    """Exercise domain, application, presentation, and persistence boundaries."""

    def setUp(self):
        self.firestore = FakeFirestoreClient()
        self.events = RecordingPublisher()
        self.repository = FirestoreTaskRepository(self.firestore)
        self.service = TaskService(
            self.repository,
            FixedClock(),
            UUIDGenerator(),
            self.events,
            TaskOrdering(),
        )
        self.routes = TaskRoutes(TaskController(self.service))
        self.user = AuthenticatedUser(UserId("firebase-user-a"), "a@example.com")
        self.other_user = AuthenticatedUser(UserId("firebase-user-b"), "b@example.com")

    def request(self, method: str, path: str, body=None, user=None):
        """Dispatch a request as the default authenticated test user."""
        return self.routes.dispatch(method, path, body, user or self.user)

    def test_full_crud_and_complete_flow(self):
        status, first = self.request("POST", "/tasks", {"title": "  Read DDD  "})
        self.assertEqual(status, 201)
        self.assertEqual(first["title"], "Read DDD")

        status, fetched = self.request("GET", f"/tasks/{first['id']}")
        self.assertEqual((status, fetched), (200, first))

        status, updated = self.request(
            "PATCH", f"/tasks/{first['id']}", {"title": "Learn onion architecture"}
        )
        self.assertEqual(status, 200)
        self.assertEqual(updated["title"], "Learn onion architecture")

        _, second = self.request("POST", "/tasks", {"title": "Write tests"})
        complete_path = f"/tasks/{first['id']}/complete"
        status, completed = self.request("POST", complete_path)
        self.assertEqual(status, 200)
        self.assertEqual(completed["completed_at"], FixedClock().now().isoformat())
        self.assertEqual(self.request("POST", complete_path)[1], completed)
        self.assertEqual(len(self.events.events), 1)

        _, result = self.request("GET", "/tasks")
        self.assertEqual(
            [task["id"] for task in result["tasks"]], [second["id"], first["id"]]
        )

        status, deleted = self.request("DELETE", f"/tasks/{second['id']}")
        self.assertEqual(status, 200)
        self.assertEqual(deleted, {"id": second["id"], "deleted": True})
        with self.assertRaises(TaskNotFound):
            self.request("GET", f"/tasks/{second['id']}")

    def test_each_user_can_access_only_their_own_tasks(self):
        _, owned = self.request("POST", "/tasks", {"title": "Private task"})
        _, other_list = self.request("GET", "/tasks", user=self.other_user)
        self.assertEqual(other_list, {"tasks": []})

        for method, path, body in [
            ("GET", f"/tasks/{owned['id']}", None),
            ("PATCH", f"/tasks/{owned['id']}", {"title": "Stolen"}),
            ("POST", f"/tasks/{owned['id']}/complete", None),
            ("DELETE", f"/tasks/{owned['id']}", None),
        ]:
            with self.subTest(method=method):
                with self.assertRaises(TaskNotFound):
                    self.request(method, path, body, self.other_user)

        self.assertEqual(self.request("GET", f"/tasks/{owned['id']}")[1], owned)

    def test_invalid_title_never_persists(self):
        for title in ["", "   ", "x" * 121]:
            with self.subTest(title=title):
                with self.assertRaises(InvalidTask):
                    self.service.create(CreateTaskDTO(title), self.user.id)
        self.assertEqual(self.service.list_tasks(self.user.id), [])
        self.assertEqual(TaskTitle(" a "), TaskTitle("a"))

    def test_transport_validation_missing_task_and_routes(self):
        for body in [None, [], {"title": 1}, {"title": "a", "extra": True}]:
            with self.assertRaises(InvalidRequest):
                self.request("POST", "/tasks", body)
        with self.assertRaises(TaskNotFound):
            self.service.complete(str(uuid4()), self.user.id)
        with self.assertRaises(InvalidTask):
            self.service.complete("not-a-uuid", self.user.id)
        self.assertEqual(self.request("PUT", "/tasks")[0], 405)
        self.assertEqual(self.request("GET", "/unknown")[0], 404)

    def test_firestore_round_trip_restores_domain_values(self):
        dto = self.service.create(CreateTaskDTO("Buy Bob's notebook"), self.user.id)
        self.service.complete(dto.id, self.user.id)
        restored = TaskService(
            FirestoreTaskRepository(self.firestore), FixedClock(), UUIDGenerator(),
            self.events, TaskOrdering(),
        )
        task = restored.list_tasks(self.user.id)[0]
        self.assertEqual(task.title, "Buy Bob's notebook")
        self.assertIsNotNone(task.completed_at)

    def test_every_saved_document_has_the_complete_field_contract(self):
        created = self.service.create(CreateTaskDTO("Check document contract"), self.user.id)
        stored = self.firestore.collections["tasks"][created.id]
        self.assertEqual(set(stored), TASK_DOCUMENT_FIELDS)
        self.assertIsNone(stored["completed_at"])
        self.assertEqual(stored["owner_id"], self.user.id.value)

        self.service.complete(created.id, self.user.id)
        completed = self.firestore.collections["tasks"][created.id]
        self.assertEqual(set(completed), TASK_DOCUMENT_FIELDS)
        self.assertIsNotNone(completed["completed_at"])

    def test_every_task_response_has_the_same_fields(self):
        expected_fields = {"id", "title", "created_at", "completed_at"}
        _, created = self.request("POST", "/tasks", {"title": "Check response contract"})
        _, listed = self.request("GET", "/tasks")
        _, fetched = self.request("GET", f"/tasks/{created['id']}")
        _, updated = self.request(
            "PATCH", f"/tasks/{created['id']}", {"title": "Updated contract"}
        )
        _, completed = self.request("POST", f"/tasks/{created['id']}/complete")

        self.assertEqual(set(created), expected_fields)
        self.assertTrue(all(set(task) == expected_fields for task in listed["tasks"]))
        self.assertEqual(set(fetched), expected_fields)
        self.assertEqual(set(updated), expected_fields)
        self.assertEqual(set(completed), expected_fields)

    def test_legacy_unowned_document_is_inaccessible(self):
        task_id = "00000000-0000-0000-0000-000000000201"
        self.firestore.collections.setdefault("tasks", {})[task_id] = {
            "title": "Legacy pending task",
            "created_at": FixedClock().now(),
            "completed_at": None,
            "owner_id": None,
        }
        self.assertIsNone(self.repository.get(TaskId(task_id), self.user.id))
        self.assertEqual(self.repository.list_all(self.user.id), [])

    def test_source_dependencies_point_inward(self):
        root = Path(__file__).resolve().parents[1]
        forbidden = {
            "domain": {"application", "infrastructure", "presentation", "firebase_admin", "http"},
            "application": {"infrastructure", "presentation", "firebase_admin", "http"},
            "infrastructure": {"presentation"},
            "presentation": {"infrastructure", "firebase_admin"},
        }
        for layer, disallowed in forbidden.items():
            for file in (root / layer).rglob("*.py"):
                tree = ast.parse(file.read_text())
                imports = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        imports.extend(alias.name.split(".")[0] for alias in node.names)
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        imports.append(node.module.split(".")[0])
                self.assertFalse(set(imports) & disallowed, str(file))


if __name__ == "__main__":
    unittest.main()
