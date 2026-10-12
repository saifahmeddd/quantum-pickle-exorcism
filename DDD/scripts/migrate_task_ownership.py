"""Audit, add, or roll back the nullable owner_id field on legacy tasks."""

import argparse

from firebase_admin import firestore

from infrastructure.config.settings import Settings
from infrastructure.firebase.client import create_firestore_client


def parse_args() -> argparse.Namespace:
    """Require an explicit mutation mode; no flag performs a read-only audit."""
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--apply",
        action="store_true",
        help="Add owner_id=null only to documents that do not have the field.",
    )
    mode.add_argument(
        "--rollback",
        action="store_true",
        help="Remove owner_id only when its current value is null.",
    )
    return parser.parse_args()


def main() -> None:
    """Run an idempotent ownership-schema audit or migration."""
    args = parse_args()
    settings = Settings.from_environment()
    client = create_firestore_client(
        settings.firebase_project_id, settings.firebase_credentials_path
    )
    snapshots = list(client.collection(settings.task_collection).stream())
    missing = 0
    null = 0
    assigned = 0
    changed = 0

    for snapshot in snapshots:
        data = snapshot.to_dict() or {}
        if "owner_id" not in data:
            missing += 1
            if args.apply:
                snapshot.reference.set({"owner_id": None}, merge=True)
                changed += 1
        elif data["owner_id"] is None:
            null += 1
            if args.rollback:
                snapshot.reference.update({"owner_id": firestore.DELETE_FIELD})
                changed += 1
        else:
            assigned += 1

    mode = "apply" if args.apply else "rollback" if args.rollback else "audit"
    print(
        f"mode={mode} total={len(snapshots)} missing={missing} "
        f"null={null} assigned={assigned} changed={changed}"
    )


if __name__ == "__main__":
    main()
