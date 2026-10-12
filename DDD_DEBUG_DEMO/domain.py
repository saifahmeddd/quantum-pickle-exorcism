"""Domain layer: pure TODO business objects and rules."""

from dataclasses import dataclass  # Dataclasses keep the example compact.
from datetime import datetime  # The task records when it was created.


@dataclass(frozen=True)
class TaskTitle:
    """A value object that guarantees every task title is valid."""

    value: str  # The domain-owned title value.

    def __post_init__(self) -> None:
        """Enforce the title business rule whenever a title is created."""
        normalized = self.value.strip()  # Domain removes accidental whitespace.
        if not 1 <= len(normalized) <= 120:  # Domain owns the 1–120 rule.
            raise ValueError("Task title must contain 1 to 120 characters.")
        object.__setattr__(self, "value", normalized)  # Save normalized value.


@dataclass(frozen=True)
class Task:
    """Task entity created only from valid domain values."""

    id: str  # Identity distinguishes this task from every other task.
    title: TaskTitle  # Value object guarantees title validity.
    created_at: datetime  # Creation time is supplied by the application.

    @classmethod
    def create(cls, task_id: str, raw_title: str, now: datetime) -> "Task":
        """Create a task while applying the domain title rule."""
        title = TaskTitle(raw_title)  # Constructing the value object runs its rule.
        return cls(task_id, title, now)  # Return a valid domain entity.
