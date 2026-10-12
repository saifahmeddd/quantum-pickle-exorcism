"""Application service coordinating registration and login use cases."""

from application.dtos.auth_dto import (
    AuthSessionDTO,
    LoginUserDTO,
    RegisterUserDTO,
)
from application.interfaces.identity_provider import IdentityProvider


class AuthService:
    """Delegate credential workflows through an injected identity-provider port."""

    def __init__(self, identity_provider: IdentityProvider):
        self.identity_provider = identity_provider

    def register(self, command: RegisterUserDTO) -> AuthSessionDTO:
        """Register a new user and return the resulting Firebase session."""
        return self.identity_provider.register(command)

    def login(self, command: LoginUserDTO) -> AuthSessionDTO:
        """Authenticate a registered user and return a Firebase session."""
        return self.identity_provider.login(command)
