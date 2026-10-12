from copy import deepcopy


class FakeDocumentSnapshot:
    def __init__(self, document_id: str, data: dict | None):
        self.id = document_id
        self.exists = data is not None
        self._data = deepcopy(data)

    def to_dict(self) -> dict | None:
        return deepcopy(self._data)


class FakeDocumentReference:
    def __init__(self, documents: dict[str, dict], document_id: str):
        self.documents = documents
        self.id = document_id

    def set(self, data: dict) -> None:
        self.documents[self.id] = deepcopy(data)

    def get(self) -> FakeDocumentSnapshot:
        return FakeDocumentSnapshot(self.id, self.documents.get(self.id))


class FakeCollectionReference:
    def __init__(self, documents: dict[str, dict]):
        self.documents = documents

    def document(self, document_id: str) -> FakeDocumentReference:
        return FakeDocumentReference(self.documents, document_id)

    def stream(self):
        for document_id, data in list(self.documents.items()):
            yield FakeDocumentSnapshot(document_id, data)


class FakeFirestoreClient:
    def __init__(self):
        self.collections: dict[str, dict[str, dict]] = {}

    def collection(self, name: str) -> FakeCollectionReference:
        return FakeCollectionReference(self.collections.setdefault(name, {}))

