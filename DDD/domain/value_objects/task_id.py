"""Validated identity value used by the Task aggregate."""

from dataclasses import dataclass
from uuid import UUID

from domain.exceptions.task_errors import InvalidTask


@dataclass(frozen=True)
class TaskId:
    """Immutable task UUID stored in canonical text form."""

    value: str

    def __post_init__(self) -> None:
        """Reject invalid UUID input and normalize valid values."""
        try:
            normalized = str(UUID(self.value))
        except (ValueError, TypeError, AttributeError):
            raise InvalidTask("Task ID must be a UUID.") from None
        object.__setattr__(self, "value", normalized)
