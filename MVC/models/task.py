from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


class InvalidTask(ValueError):
    """A task value violates a model rule."""


@dataclass
class Task:
    """Model object containing TODO state and business behavior."""

    id: str
    title: str
    created_at: datetime
    completed_at: datetime | None = None

    def __post_init__(self) -> None:
        try:
            self.id = str(UUID(self.id))
        except (ValueError, TypeError, AttributeError):
            raise InvalidTask("Task ID must be a UUID.") from None

        if not isinstance(self.title, str):
            raise InvalidTask("Title must be text.")
        self.title = self.title.strip()
        if not 1 <= len(self.title) <= 120:
            raise InvalidTask("Title must contain 1–120 characters.")

    def complete(self, now: datetime) -> bool:
        """Complete once; return whether state actually changed."""
        if self.completed_at is not None:
            return False
        self.completed_at = now
        return True

