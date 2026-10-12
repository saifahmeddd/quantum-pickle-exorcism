"""Firebase Admin adapter that verifies client-issued Firebase ID tokens."""

from application.exceptions.authentication_failed import AuthenticationFailed
from application.interfaces.authentication import AuthenticatedUser
from domain.exceptions.task_errors import InvalidUserId
from domain.value_objects.user_id import UserId


class FirebaseTokenVerifier:
    """Turn a valid, current Firebase ID token into a trusted application user."""

    def verify(self, token: str) -> AuthenticatedUser:
        """Validate signature, audience, expiry, revocation, and user status."""
        from firebase_admin import auth

        try:
            claims = auth.verify_id_token(token, check_revoked=True)
            raw_user_id = claims.get("uid") or claims.get("sub")
            user_id = UserId(raw_user_id)
        except (
            auth.InvalidIdTokenError,
            auth.ExpiredIdTokenError,
            auth.RevokedIdTokenError,
            auth.UserDisabledError,
            InvalidUserId,
            ValueError,
        ) as exc:
            raise AuthenticationFailed(
                "The Firebase ID token is invalid, expired, or revoked."
            ) from exc

        email = claims.get("email")
        return AuthenticatedUser(
            id=user_id,
            email=email if isinstance(email, str) else None,
        )
