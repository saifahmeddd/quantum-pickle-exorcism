import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    firebase_project_id: str | None = None
    task_collection: str = "tasks"
    host: str = "127.0.0.1"
    port: int = 8000

    @classmethod
    def from_environment(cls) -> "Settings":
        return cls(
            os.getenv("FIREBASE_PROJECT_ID") or None,
            os.getenv("FIREBASE_TASK_COLLECTION", "tasks"),
            os.getenv("TODO_HOST", "127.0.0.1"),
            int(os.getenv("TODO_PORT", "8000")),
        )
