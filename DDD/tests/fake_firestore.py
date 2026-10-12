"""In-memory test doubles for the small Firestore API surface we consume."""

from copy import deepcopy


class FakeDocumentSnapshot:
    """Immutable-style view of one stored fake document."""

    def __init__(self, document_id: str, data: dict | None):
        self.id = document_id
        self.exists = data is not None
        self._data = deepcopy(data)

    def to_dict(self) -> dict | None:
        return deepcopy(self._data)


class FakeDocumentReference:
    """Read and replace one document in the fake store."""

    def __init__(self, documents: dict[str, dict], document_id: str):
        self.documents = documents
        self.id = document_id

    def set(self, data: dict) -> None:
        self.documents[self.id] = deepcopy(data)

    def get(self) -> FakeDocumentSnapshot:
        return FakeDocumentSnapshot(self.id, self.documents.get(self.id))

    def delete(self) -> None:
        """Remove this document when it exists, matching Firestore semantics."""
        self.documents.pop(self.id, None)


class FakeQuery:
    """Evaluate the equality query used for owner-scoped task lists."""

    def __init__(self, documents: dict[str, dict], field: str, value: object):
        self.documents = documents
        self.field = field
        self.value = value

    def stream(self):
        for document_id, data in list(self.documents.items()):
            if data.get(self.field) == self.value:
                yield FakeDocumentSnapshot(document_id, data)


class FakeCollectionReference:
    """Address documents and stream snapshots from one fake collection."""

    def __init__(self, documents: dict[str, dict]):
        self.documents = documents

    def document(self, document_id: str) -> FakeDocumentReference:
        return FakeDocumentReference(self.documents, document_id)

    def stream(self):
        for document_id, data in list(self.documents.items()):
            yield FakeDocumentSnapshot(document_id, data)

    def where(self, *, filter) -> FakeQuery:
        """Create the one equality query needed by the repository adapter."""
        if filter.op_string != "==":
            raise NotImplementedError("The fake supports equality queries only.")
        return FakeQuery(self.documents, filter.field_path, filter.value)


class FakeFirestoreClient:
    """Keep named Firestore-like collections entirely in memory."""

    def __init__(self):
        self.collections: dict[str, dict[str, dict]] = {}

    def collection(self, name: str) -> FakeCollectionReference:
        return FakeCollectionReference(self.collections.setdefault(name, {}))
