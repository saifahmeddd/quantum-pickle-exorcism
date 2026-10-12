"""Request-scoped logging behavior shared by all HTTP routes."""

import logging
from uuid import uuid4


def begin_request(method: str, path: str) -> str:
    """Create a correlation ID and log the beginning of one request."""
    request_id = str(uuid4())
    logging.getLogger(__name__).info("request_id=%s %s %s", request_id, method, path)
    return request_id
