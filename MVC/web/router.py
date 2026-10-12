import re

from controllers.task_controller import TaskController
from views.task_view import error_view


class Router:
    """Match HTTP method/path pairs and dispatch controller actions."""

    def __init__(self, tasks: TaskController):
        self.tasks = tasks

    def dispatch(self, method: str, path: str, body: object) -> tuple[int, dict]:
        if path == "/tasks":
            if method == "GET":
                return self.tasks.index()
            if method == "POST":
                return self.tasks.create(body)
            return self.tasks.method_not_allowed()

        match = re.fullmatch(r"/tasks/([^/]+)/complete", path)
        if match:
            if method == "POST":
                return self.tasks.complete(match.group(1))
            return self.tasks.method_not_allowed()

        return 404, error_view("Route not found.")

