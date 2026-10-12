"""Composition root that connects concrete adapters to application ports."""

from typing import TYPE_CHECKING

from application.interfaces.identity_provider import IdentityProvider
from application.services.auth_service import AuthService
from application.services.task_service import TaskService
from domain.domain_services.task_ordering import TaskOrdering
from infrastructure.config.settings import Settings
from infrastructure.authentication.firebase_auth_rest_provider import FirebaseAuthRestProvider
from infrastructure.firebase.client import create_firestore_client
from infrastructure.messaging.log_event_publisher import LogEventPublisher
from infrastructure.providers.system_runtime import SystemClock, UUIDGenerator
from infrastructure.repositories.firestore_task_repository import FirestoreTaskRepository
from presentation.controllers.auth_controller import AuthController
from presentation.controllers.task_controller import TaskController
from presentation.routes.api_routes import ApiRoutes
from presentation.routes.auth_routes import AuthRoutes
from presentation.routes.task_routes import TaskRoutes

if TYPE_CHECKING:
    from google.cloud.firestore_v1.client import Client


def build_routes(
    settings: Settings,
    firestore_client: "Client | None" = None,
    identity_provider: IdentityProvider | None = None,
) -> ApiRoutes:
    """Build the fully wired request handler used by the HTTP server."""
    client = firestore_client or create_firestore_client(
        settings.firebase_project_id,
        settings.firebase_credentials_path,
    )
    repository = FirestoreTaskRepository(client, settings.task_collection)
    service = TaskService(
        repository,
        SystemClock(),
        UUIDGenerator(),
        LogEventPublisher(),
        TaskOrdering(),
    )
    task_routes = TaskRoutes(TaskController(service))

    # The application depends on its IdentityProvider port; this outer
    # composition root chooses Firebase as the concrete implementation.
    provider = identity_provider or FirebaseAuthRestProvider(
        settings.firebase_web_api_key
    )
    auth_routes = AuthRoutes(AuthController(AuthService(provider)))
    return ApiRoutes(auth_routes, task_routes)
