"""Immutable facts emitted after meaningful task state changes."""

from dataclasses import dataclass
from datetime import datetime

from domain.value_objects.task_id import TaskId


@dataclass(frozen=True)
class TaskCompleted:
    """Record that a task was completed at a specific time."""

    task_id: TaskId
    occurred_at: datetime
