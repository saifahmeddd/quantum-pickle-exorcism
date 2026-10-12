"""Top-level route composition for public auth and protected task requests."""

from application.exceptions.authentication_failed import AuthenticationFailed
from application.interfaces.authentication import AuthenticatedUser
from presentation.routes.auth_routes import AUTH_PATHS, AuthRoutes
from presentation.routes.task_routes import TaskRoutes


class ApiRoutes:
    """Select an auth or task route while preserving task authorization."""

    def __init__(self, auth_routes: AuthRoutes, task_routes: TaskRoutes):
        self.auth_routes = auth_routes
        self.task_routes = task_routes

    def requires_authentication(self, path: str) -> bool:
        """Only exact register and login paths are public."""
        return path not in AUTH_PATHS

    def dispatch(
        self,
        method: str,
        path: str,
        body: object,
        user: AuthenticatedUser | None,
    ) -> tuple[int, dict]:
        """Dispatch a request to its presentation route group."""
        if path in AUTH_PATHS:
            return self.auth_routes.dispatch(method, path, body)
        if user is None:
            raise AuthenticationFailed("A verified user is required.")
        return self.task_routes.dispatch(method, path, body, user)
