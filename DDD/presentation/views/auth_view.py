"""JSON-ready views for successful authentication use cases."""

from dataclasses import asdict

from application.dtos.auth_dto import AuthSessionDTO


def auth_session_view(session: AuthSessionDTO) -> dict:
    """Convert the application output DTO to the public JSON response shape."""
    return asdict(session)
