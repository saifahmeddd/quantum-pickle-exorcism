"""JSON-ready representations returned by task HTTP endpoints."""

from dataclasses import asdict

from application.dtos.task_dto import TaskDTO


def task_view(task: TaskDTO) -> dict:
    """Render one application DTO without exposing domain objects."""
    return asdict(task)


def tasks_view(tasks: list[TaskDTO]) -> dict:
    """Render the task collection under a stable top-level key."""
    return {"tasks": [task_view(task) for task in tasks]}


def error_view(message: str) -> dict:
    """Render a client-safe error response."""
    return {"error": message}


def deleted_view(task_id: str) -> dict:
    """Confirm which task resource was deleted."""
    return {"id": task_id, "deleted": True}
