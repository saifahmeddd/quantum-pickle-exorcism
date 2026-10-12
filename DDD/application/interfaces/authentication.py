"""Authentication port and verified identity passed into protected use cases."""

from dataclasses import dataclass
from typing import Protocol

from domain.value_objects.user_id import UserId


@dataclass(frozen=True)
class AuthenticatedUser:
    """Identity claims trusted only after a token verifier validates them."""

    id: UserId
    email: str | None = None


class TokenVerifier(Protocol):
    """Verify a client token and return the authenticated application identity."""

    def verify(self, token: str) -> AuthenticatedUser: ...
