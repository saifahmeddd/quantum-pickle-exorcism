"""Environment-backed settings used only by the outer application boundary."""

import os
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CREDENTIALS_PATH = PROJECT_ROOT / ".secrets" / "firebase-service-account.json"


@dataclass(frozen=True)
class Settings:
    """Immutable Firebase and HTTP configuration for one application process."""

    firebase_project_id: str | None = None
    firebase_credentials_path: str | None = None
    firebase_web_api_key: str | None = None
    task_collection: str = "tasks"
    host: str = "127.0.0.1"
    port: int = 8000

    @classmethod
    def from_environment(cls) -> "Settings":
        """Load settings, preferring explicit credentials over the local key."""
        configured_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        local_credentials = (
            str(DEFAULT_CREDENTIALS_PATH) if DEFAULT_CREDENTIALS_PATH.is_file() else None
        )
        return cls(
            firebase_project_id=os.getenv("FIREBASE_PROJECT_ID") or None,
            firebase_credentials_path=configured_credentials or local_credentials,
            firebase_web_api_key=os.getenv("FIREBASE_WEB_API_KEY") or None,
            task_collection=os.getenv("FIREBASE_TASK_COLLECTION", "tasks"),
            host=os.getenv("TODO_HOST", "127.0.0.1"),
            port=int(os.getenv("TODO_PORT", "8000")),
        )
