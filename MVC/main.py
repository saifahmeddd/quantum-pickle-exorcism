import logging

from config.settings import Settings
from controllers.task_controller import TaskController
from firebase.client import create_firestore_client
from models.task_store import TaskStore
from web.http_server import make_server
from web.router import Router


def main() -> None:
    """Composition root: construct MVC collaborators and start the web app."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    settings = Settings.from_environment()
    client = create_firestore_client(settings.firebase_project_id)
    store = TaskStore(client, settings.task_collection)
    router = Router(TaskController(store))

    with make_server(settings.host, settings.port, router) as server:
        logging.info("MVC TODO API listening on http://%s:%s", settings.host, settings.port)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
