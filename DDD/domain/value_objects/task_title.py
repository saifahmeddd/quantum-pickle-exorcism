"""Validated title value used by the Task aggregate."""

from dataclasses import dataclass

from domain.exceptions.task_errors import InvalidTask


@dataclass(frozen=True)
class TaskTitle:
    """Immutable normalized title containing 1–120 characters."""

    value: str

    def __post_init__(self) -> None:
        """Trim surrounding whitespace and enforce the title invariant."""
        if not isinstance(self.value, str):
            raise InvalidTask("Title must be text.")
        normalized = self.value.strip()
        if not 1 <= len(normalized) <= 120:
            raise InvalidTask("Title must contain 1–120 characters.")
        object.__setattr__(self, "value", normalized)
