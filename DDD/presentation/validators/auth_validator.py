"""Validation at the HTTP boundary for credential request bodies."""

from presentation.validators.task_validator import InvalidRequest


def validate_credentials(body: object) -> tuple[str, str]:
    """Return normalized credentials from an exact email/password JSON object."""
    if not isinstance(body, dict):
        raise InvalidRequest("Body must be a JSON object.")
    if set(body) != {"email", "password"}:
        raise InvalidRequest("Body must contain only email and password.")

    email = body["email"]
    password = body["password"]
    if not isinstance(email, str) or not email.strip():
        raise InvalidRequest("Email must be a non-empty string.")
    if not isinstance(password, str) or not password:
        raise InvalidRequest("Password must be a non-empty string.")

    # Email surrounding whitespace is accidental input. Password bytes are kept
    # exactly as supplied because whitespace may be part of a valid password.
    return email.strip(), password
