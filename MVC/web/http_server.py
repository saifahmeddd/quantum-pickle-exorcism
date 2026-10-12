import json
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlsplit

from controllers.request_validator import InvalidRequest
from models.task import InvalidTask
from models.task_store import TaskNotFound
from views.task_view import error_view
from web.middleware import begin_request
from web.router import Router


def make_server(host: str, port: int, router: Router) -> HTTPServer:
    """Build the HTTP boundary around the MVC components."""

    class Handler(BaseHTTPRequestHandler):
        def handle_request(self) -> None:
            path = urlsplit(self.path).path
            request_id = begin_request(self.command, path)
            try:
                body = self._read_body()
                status, payload = router.dispatch(self.command, path, body)
            except (InvalidRequest, InvalidTask, json.JSONDecodeError, UnicodeDecodeError) as exc:
                status, payload = 400, error_view(str(exc))
            except TaskNotFound as exc:
                status, payload = 404, error_view(str(exc))
            except Exception:
                logging.getLogger(__name__).exception("request_id=%s failed", request_id)
                status, payload = 500, error_view("Internal server error.")

            encoded = json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(encoded)))
            self.send_header("X-Request-ID", request_id)
            self.end_headers()
            self.wfile.write(encoded)

        def _read_body(self) -> object:
            if self.command != "POST":
                return None
            try:
                length = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                raise InvalidRequest("Invalid Content-Length.") from None
            if not 0 <= length <= 16384:
                raise InvalidRequest("Body must be at most 16 KiB.")
            if not length:
                return None
            if self.headers.get_content_type() != "application/json":
                raise InvalidRequest("Use Content-Type: application/json.")
            return json.loads(self.rfile.read(length))

        do_GET = handle_request
        do_POST = handle_request
        do_PUT = handle_request
        do_PATCH = handle_request
        do_DELETE = handle_request

    # This teaching server is intentionally single-threaded for a clear flow.
    return HTTPServer((host, port), Handler)
