"""Business policies that operate across multiple task entities."""

from collections.abc import Iterable

from domain.entities.task import Task


class TaskOrdering:
    """Domain service: unfinished tasks precede completed tasks.

    The policy spans multiple Task entities and has no persistence or transport
    concern, so it belongs in the domain layer rather than infrastructure.
    """

    def order(self, tasks: Iterable[Task]) -> list[Task]:
        """Return unfinished tasks first, then order by age and stable ID."""
        return sorted(
            tasks,
            key=lambda task: (
                task.completed_at is not None,
                task.created_at,
                task.id.value,
            ),
        )
