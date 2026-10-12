from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from models.task import InvalidTask, Task


class TaskNotFound(LookupError):
    """The requested model does not exist."""


class TaskStore:
    """Firestore-backed Model persistence and queries for tasks.

    Classic MVC treats persistence as part of the Model. This class keeps
    Firebase details out of controllers while returning Task model objects.
    """

    def __init__(
        self,
        client: Any,
        collection_name: str = "tasks",
        clock=None,
        id_factory=None,
    ):
        self.collection = client.collection(collection_name)
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        self.id_factory = id_factory or (lambda: str(uuid4()))

    def create(self, title: str) -> Task:
        task = Task(self.id_factory(), title, self.clock())
        self._save(task)
        return task

    def list_all(self) -> list[Task]:
        tasks = [self._from_snapshot(snapshot) for snapshot in self.collection.stream()]
        return sorted(
            tasks,
            key=lambda task: (
                task.completed_at is not None,
                task.created_at,
                task.id,
            ),
        )

    def complete(self, task_id: str) -> Task:
        try:
            canonical_id = str(UUID(task_id))
        except (ValueError, TypeError, AttributeError):
            raise InvalidTask("Task ID must be a UUID.") from None

        snapshot = self.collection.document(canonical_id).get()
        if not snapshot.exists:
            raise TaskNotFound("Task not found.")

        task = self._from_snapshot(snapshot)
        if task.complete(self.clock()):
            self._save(task)
        return task

    def _save(self, task: Task) -> None:
        self.collection.document(task.id).set(
            {
                "title": task.title,
                "created_at": task.created_at,
                "completed_at": task.completed_at,
            }
        )

    @staticmethod
    def _from_snapshot(snapshot: Any) -> Task:
        data = snapshot.to_dict()
        return Task(
            snapshot.id,
            data["title"],
            _as_datetime(data["created_at"]),
            _as_datetime(data["completed_at"])
            if data.get("completed_at") is not None
            else None,
        )


def _as_datetime(value: Any) -> datetime:
    """Accept Firestore datetimes and ISO strings from older/manual documents."""
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        return datetime.fromisoformat(value)
    raise ValueError("Firestore task timestamp must be a datetime or ISO string.")

