from typing import Any


def create_firestore_client(project_id: str | None = None) -> Any:
    """Initialize Firebase once and return its Cloud Firestore client."""
    import firebase_admin
    from firebase_admin import firestore

    try:
        app = firebase_admin.get_app()
    except ValueError:
        options = {"projectId": project_id} if project_id else None
        app = firebase_admin.initialize_app(options=options)
    return firestore.client(app=app)

