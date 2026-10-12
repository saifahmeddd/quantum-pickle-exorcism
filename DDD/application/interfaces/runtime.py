"""Ports for runtime values and event delivery required by use cases."""

from datetime import datetime
from typing import Protocol

from domain.domain_events.task_completed import TaskCompleted
from domain.value_objects.task_id import TaskId


class Clock(Protocol):
    """Provide time without coupling use cases to the system clock."""

    def now(self) -> datetime: ...


class IdGenerator(Protocol):
    """Provide task identities without choosing an ID technology."""

    def new_id(self) -> TaskId: ...


class EventPublisher(Protocol):
    """Deliver domain events without choosing a messaging technology."""

    def publish(self, event: TaskCompleted) -> None: ...
