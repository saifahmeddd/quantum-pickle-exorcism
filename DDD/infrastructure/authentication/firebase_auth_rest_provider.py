"""Firebase Auth REST adapter for backend-mediated registration and login."""

import json
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from application.dtos.auth_dto import (
    AuthSessionDTO,
    LoginUserDTO,
    RegisterUserDTO,
)
from application.exceptions.identity_errors import (
    IdentityProviderUnavailable,
    LoginFailed,
    RegistrationFailed,
)


FIREBASE_AUTH_BASE_URL = "https://identitytoolkit.googleapis.com/v1/accounts"


@dataclass(frozen=True)
class _FirebaseAuthError(Exception):
    """Private representation of an error returned by Firebase Auth REST."""

    code: str


class FirebaseAuthRestProvider:
    """Implement identity use cases through Firebase's official REST API."""

    def __init__(self, web_api_key: str | None):
        self.web_api_key = web_api_key

    def register(self, command: RegisterUserDTO) -> AuthSessionDTO:
        """Create a Firebase email/password user and return its session."""
        try:
            response = self._post(
                "signUp",
                {"email": command.email, "password": command.password},
            )
        except _FirebaseAuthError as exc:
            raise RegistrationFailed(_registration_message(exc.code)) from None
        return _to_session(response)

    def login(self, command: LoginUserDTO) -> AuthSessionDTO:
        """Authenticate a Firebase email/password user and return its session."""
        try:
            response = self._post(
                "signInWithPassword",
                {"email": command.email, "password": command.password},
            )
        except _FirebaseAuthError as exc:
            raise LoginFailed(_login_message(exc.code)) from None
        return _to_session(response)

    def _post(self, action: str, credentials: dict[str, str]) -> dict:
        """Send one bounded JSON credential request without logging its body."""
        if not self.web_api_key:
            raise IdentityProviderUnavailable(
                "FIREBASE_WEB_API_KEY is required for register and login."
            )

        url = f"{FIREBASE_AUTH_BASE_URL}:{action}?{urlencode({'key': self.web_api_key})}"
        payload = {**credentials, "returnSecureToken": True}
        request = Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urlopen(request, timeout=10) as response:
                result = json.loads(response.read())
        except HTTPError as exc:
            code = _firebase_error_code(exc)
            if exc.code >= 500 or code in {
                "API_KEY_INVALID",
                "CONFIGURATION_NOT_FOUND",
            }:
                raise IdentityProviderUnavailable(
                    "Firebase Authentication is not configured or available."
                ) from None
            raise _FirebaseAuthError(code) from None
        except (URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise IdentityProviderUnavailable(
                "Firebase Authentication is temporarily unavailable."
            ) from exc

        if not isinstance(result, dict):
            raise IdentityProviderUnavailable(
                "Firebase Authentication returned an invalid response."
            )
        return result


def _firebase_error_code(error: HTTPError) -> str:
    """Extract only Firebase's stable error code from an unsuccessful response."""
    try:
        payload = json.loads(error.read())
        message = payload.get("error", {}).get("message", "")
        if isinstance(message, str) and message:
            return message.split(" : ", 1)[0]
    except (AttributeError, json.JSONDecodeError):
        pass
    return "UNKNOWN"


def _to_session(response: dict) -> AuthSessionDTO:
    """Map a successful Firebase response to the application output DTO."""
    try:
        return AuthSessionDTO(
            user_id=_required_text(response, "localId"),
            email=_required_text(response, "email"),
            id_token=_required_text(response, "idToken"),
            refresh_token=_required_text(response, "refreshToken"),
            expires_in=int(_required_text(response, "expiresIn")),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise IdentityProviderUnavailable(
            "Firebase Authentication returned an incomplete response."
        ) from exc


def _required_text(response: dict, field: str) -> str:
    """Return a required non-empty string from a Firebase response."""
    value = response[field]
    if not isinstance(value, str) or not value:
        raise ValueError(f"Missing Firebase response field: {field}")
    return value


def _registration_message(code: str) -> str:
    """Translate provider codes into stable client-safe registration messages."""
    if code == "EMAIL_EXISTS":
        return "Email is already registered."
    if code == "INVALID_EMAIL":
        return "Email address is invalid."
    if code == "OPERATION_NOT_ALLOWED" or code == "ADMIN_ONLY_OPERATION":
        return "Email/password registration is disabled."
    if code == "WEAK_PASSWORD":
        return "Password does not meet Firebase requirements."
    return "Registration failed."


def _login_message(code: str) -> str:
    """Translate provider codes without revealing whether an account exists."""
    if code == "USER_DISABLED":
        return "User account is disabled."
    if code == "OPERATION_NOT_ALLOWED":
        return "Email/password login is disabled."
    return "Invalid email or password."
