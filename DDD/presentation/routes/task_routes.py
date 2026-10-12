"""HTTP route table for task resources and actions."""

import re

from presentation.controllers.task_controller import TaskController
from application.interfaces.authentication import AuthenticatedUser


COMPLETE_TASK_PATH = re.compile(r"/tasks/([^/]+)/complete")
TASK_PATH = re.compile(r"/tasks/([^/]+)")


class TaskRoutes:
    """Dispatch supported method/path pairs to task controller actions."""

    def __init__(self, controller: TaskController):
        self.controller = controller

    def dispatch(
        self,
        method: str,
        path: str,
        body: object,
        user: AuthenticatedUser,
    ) -> tuple[int, dict]:
        """Return a controller response or a route-level 404/405 response."""
        if path == "/tasks":
            if method == "GET":
                return self.controller.list_tasks(user)
            if method == "POST":
                return self.controller.create(body, user)
            return 405, {"error": "Method not allowed."}
        match = COMPLETE_TASK_PATH.fullmatch(path)
        if match:
            if method == "POST":
                return self.controller.complete(match.group(1), user)
            return 405, {"error": "Method not allowed."}
        match = TASK_PATH.fullmatch(path)
        if match:
            task_id = match.group(1)
            if method == "GET":
                return self.controller.get(task_id, user)
            if method == "PATCH":
                return self.controller.update(task_id, body, user)
            if method == "DELETE":
                return self.controller.delete(task_id, user)
            return 405, {"error": "Method not allowed."}
        return 404, {"error": "Route not found."}
