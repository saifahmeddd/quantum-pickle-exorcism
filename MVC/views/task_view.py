from models.task import Task


def task_view(task: Task) -> dict:
    """Render a Task model as a JSON-ready representation."""
    return {
        "id": task.id,
        "title": task.title,
        "created_at": task.created_at.isoformat(),
        "completed_at": task.completed_at.isoformat()
        if task.completed_at
        else None,
    }


def task_list_view(tasks: list[Task]) -> dict:
    return {"tasks": [task_view(task) for task in tasks]}


def error_view(message: str) -> dict:
    return {"error": message}

