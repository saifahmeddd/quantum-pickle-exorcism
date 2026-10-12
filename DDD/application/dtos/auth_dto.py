"""Data-only contracts for registration and login use cases."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RegisterUserDTO:
    """Email/password data entering the register-user use case."""

    email: str
    password: str


@dataclass(frozen=True)
class LoginUserDTO:
    """Email/password data entering the login-user use case."""

    email: str
    password: str


@dataclass(frozen=True)
class AuthSessionDTO:
    """Primitive Firebase session data returned to an authenticated client."""

    user_id: str
    email: str
    id_token: str
    refresh_token: str
    expires_in: int
