class InvalidRequest(ValueError):
    """The incoming request does not have the expected transport shape."""


def create_task_title(body: object) -> str:
    """Validate request shape; title business rules remain in the Model."""
    if not isinstance(body, dict) or set(body) != {"title"}:
        raise InvalidRequest("Expected a JSON object containing only title.")
    if not isinstance(body["title"], str):
        raise InvalidRequest("Title must be a string.")
    return body["title"]

