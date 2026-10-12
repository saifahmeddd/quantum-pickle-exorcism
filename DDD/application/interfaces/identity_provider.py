"""Application port for credential-based identity-provider operations."""

from typing import Protocol

from application.dtos.auth_dto import (
    AuthSessionDTO,
    LoginUserDTO,
    RegisterUserDTO,
)


class IdentityProvider(Protocol):
    """Register and authenticate users through an external identity system."""

    def register(self, command: RegisterUserDTO) -> AuthSessionDTO: ...

    def login(self, command: LoginUserDTO) -> AuthSessionDTO: ...
