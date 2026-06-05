import json
from pathlib import Path

UPLOAD_DIR = Path("data/uploads")
PROCESSED_DIR = Path("data/processed")
DOCUMENTS_DB_PATH = Path("data/documents.json")

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def load_documents() -> dict:
    if not DOCUMENTS_DB_PATH.exists():
        return {}

    with open(DOCUMENTS_DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_documents(documents: dict) -> None:
    with open(DOCUMENTS_DB_PATH, "w", encoding="utf-8") as f:
        json.dump(documents, f, ensure_ascii=False, indent=2)


def save_document_metadata(document_id: str, metadata: dict) -> None:
    documents = load_documents()
    documents[document_id] = metadata
    save_documents(documents)


def get_document_metadata(document_id: str) -> dict | None:
    documents = load_documents()
    return documents.get(document_id)


def update_document_metadata(document_id: str, updates: dict) -> None:
    documents = load_documents()

    if document_id not in documents:
        return

    documents[document_id].update(updates)
    save_documents(documents)