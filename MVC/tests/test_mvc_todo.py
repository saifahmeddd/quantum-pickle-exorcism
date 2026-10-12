import ast
import unittest
from datetime import datetime, timezone
from itertools import count
from pathlib import Path
from uuid import uuid4

from controllers.request_validator import InvalidRequest
from controllers.task_controller import TaskController
from models.task import InvalidTask, Task
from models.task_store import TaskNotFound, TaskStore
from tests.fake_firestore import FakeFirestoreClient
from web.router import Router


FIXED_TIME = datetime(2026, 1, 1, tzinfo=timezone.utc)


class TodoMvcTests(unittest.TestCase):
    def setUp(self):
        self.firestore = FakeFirestoreClient()
        self.ids = count(1)
        self.store = TaskStore(
            self.firestore,
            clock=lambda: FIXED_TIME,
            id_factory=lambda: f"00000000-0000-0000-0000-{next(self.ids):012d}",
        )
        self.router = Router(TaskController(self.store))

    def test_create_list_complete_and_repeat_completion(self):
        status, first = self.router.dispatch(
            "POST", "/tasks", {"title": "  Learn MVC  "}
        )
        self.assertEqual(status, 201)
        self.assertEqual(first["title"], "Learn MVC")
        _, second = self.router.dispatch("POST", "/tasks", {"title": "Write tests"})

        path = f"/tasks/{first['id']}/complete"
        status, completed = self.router.dispatch("POST", path, None)
        self.assertEqual(status, 200)
        self.assertEqual(completed["completed_at"], FIXED_TIME.isoformat())
        self.assertEqual(self.router.dispatch("POST", path, None)[1], completed)

        _, response = self.router.dispatch("GET", "/tasks", None)
        self.assertEqual(
            [task["id"] for task in response["tasks"]],
            [second["id"], first["id"]],
        )

    def test_model_owns_business_rules(self):
        for title in ("", "   ", "x" * 121):
            with self.subTest(title=title), self.assertRaises(InvalidTask):
                self.store.create(title)
        task = Task(str(uuid4()), "  Normalized  ", FIXED_TIME)
        self.assertEqual(task.title, "Normalized")
        self.assertTrue(task.complete(FIXED_TIME))
        self.assertFalse(task.complete(FIXED_TIME))

    def test_controller_input_and_router_errors(self):
        for body in (None, [], {"title": 1}, {"title": "a", "extra": True}):
            with self.subTest(body=body), self.assertRaises(InvalidRequest):
                self.router.dispatch("POST", "/tasks", body)
        with self.assertRaises(InvalidTask):
            self.router.dispatch("POST", "/tasks/not-a-uuid/complete", None)
        with self.assertRaises(TaskNotFound):
            self.router.dispatch(
                "POST",
                "/tasks/00000000-0000-0000-0000-000000000099/complete",
                None,
            )
        self.assertEqual(self.router.dispatch("DELETE", "/tasks", None)[0], 405)
        self.assertEqual(self.router.dispatch("GET", "/unknown", None)[0], 404)

    def test_firestore_round_trip(self):
        created = self.store.create("Buy Bob's notebook")
        self.store.complete(created.id)
        restored = self.store.list_all()[0]
        self.assertEqual(restored.title, "Buy Bob's notebook")
        self.assertEqual(restored.completed_at, FIXED_TIME)

    def test_mvc_dependency_direction(self):
        root = Path(__file__).resolve().parents[1]
        forbidden = {
            "models": {"controllers", "views", "web", "firebase_admin"},
            "views": {"controllers", "web", "firebase", "firebase_admin"},
            "controllers": {"web", "firebase", "firebase_admin"},
        }
        for folder, disallowed in forbidden.items():
            for file in (root / folder).rglob("*.py"):
                imports = []
                for node in ast.walk(ast.parse(file.read_text())):
                    if isinstance(node, ast.Import):
                        imports.extend(alias.name.split(".")[0] for alias in node.names)
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        imports.append(node.module.split(".")[0])
                self.assertFalse(set(imports) & disallowed, str(file))


if __name__ == "__main__":
    unittest.main()
