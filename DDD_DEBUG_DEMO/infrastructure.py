"""Infrastructure layer: concrete technical implementations of application ports."""

from datetime import datetime, timezone  # Concrete clock returns an aware UTC time.

from domain import Task  # Adapter stores and returns domain entities.


class InMemoryTaskRepository:
    """Small repository adapter replacing a real database for this demo."""

    def __init__(self) -> None:
        self.tasks: dict[str, Task] = {}  # Dictionary acts as temporary storage.

    def save(self, task: Task) -> None:
        """Store a task under its identity."""
        self.tasks[task.id] = task  # Concrete persistence operation.

    def get(self, task_id: str) -> Task | None:
        """Return a stored task or None when it does not exist."""
        return self.tasks.get(task_id)  # Concrete retrieval operation.


class SequentialIdGenerator:
    """Deterministic infrastructure provider used for visible debugging."""

    def __init__(self) -> None:
        self.next_number = 1  # First generated task will be task-1.

    def new_id(self) -> str:
        """Return one predictable ID and advance the counter."""
        task_id = f"task-{self.next_number}"  # Build the next identifier.
        self.next_number += 1  # Prepare the provider for another request.
        return task_id  # Return the generated value to the application.


class FixedClock:
    """Deterministic clock that makes the demonstration repeatable."""

    def now(self) -> datetime:
        """Return the same visible UTC timestamp on every run."""
        return datetime(2026, 10, 6, 12, 0, tzinfo=timezone.utc)
