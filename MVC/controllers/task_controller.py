from controllers.request_validator import create_task_title
from models.task_store import TaskStore
from views.task_view import error_view, task_view, task_list_view


class TaskController:
    """Controller actions translate input into Model calls and select Views."""

    def __init__(self, store: TaskStore):
        self.store = store

    def create(self, body: object) -> tuple[int, dict]:
        task = self.store.create(create_task_title(body))
        return 201, task_view(task)

    def index(self) -> tuple[int, dict]:
        return 200, task_list_view(self.store.list_all())

    def complete(self, task_id: str) -> tuple[int, dict]:
        return 200, task_view(self.store.complete(task_id))

    @staticmethod
    def method_not_allowed() -> tuple[int, dict]:
        return 405, error_view("Method not allowed.")

