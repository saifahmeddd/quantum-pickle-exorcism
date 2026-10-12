"""Logging implementation of the application's event-publisher port."""

import logging

from domain.domain_events.task_completed import TaskCompleted


class LogEventPublisher:
    """Local messaging adapter; replace with a broker adapter if needed."""

    def publish(self, event: TaskCompleted) -> None:
        """Write a structured completion fact to the application log."""
        logging.getLogger(__name__).info(
            "TaskCompleted task_id=%s occurred_at=%s",
            event.task_id.value, event.occurred_at.isoformat(),
        )
