"""Production providers for current time and task identity generation."""

from datetime import datetime, timezone
from uuid import uuid4

from domain.value_objects.task_id import TaskId


class SystemClock:
    """Infrastructure adapter providing wall-clock time to an application port."""

    def now(self) -> datetime:
        """Return a timezone-aware UTC timestamp."""
        return datetime.now(timezone.utc)


class UUIDGenerator:
    """Infrastructure adapter providing UUIDs to an application port."""

    def new_id(self) -> TaskId:
        """Create a random UUID wrapped in the domain value object."""
        return TaskId(str(uuid4()))
