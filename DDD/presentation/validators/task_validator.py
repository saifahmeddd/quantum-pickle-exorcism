"""Transport validation for task request payloads."""


class InvalidRequest(ValueError):
    """Malformed transport input, independent of business invariants."""


def validate_create(body: object) -> str:
    """Return the title when the create body has exactly the expected shape."""
    if not isinstance(body, dict) or set(body) != {"title"}:
        raise InvalidRequest("Expected a JSON object containing only title.")
    if not isinstance(body["title"], str):
        raise InvalidRequest("Title must be a string.")
    return body["title"]


def validate_update(body: object) -> str:
    """Return the title when the update body has exactly the expected shape."""
    if not isinstance(body, dict) or set(body) != {"title"}:
        raise InvalidRequest("Expected a JSON object containing only title.")
    if not isinstance(body["title"], str):
        raise InvalidRequest("Title must be a string.")
    return body["title"]
