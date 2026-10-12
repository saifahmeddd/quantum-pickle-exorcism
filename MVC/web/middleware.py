import logging
from uuid import uuid4


def begin_request(method: str, path: str) -> str:
    """Cross-cutting web concern shared by every route."""
    request_id = str(uuid4())
    logging.getLogger(__name__).info("request_id=%s %s %s", request_id, method, path)
    return request_id

