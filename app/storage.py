import json
from pathlib import Path
from typing import Any

DATA_DIR = Path("data")

UPLOAD_DIR = DATA_DIR / "uploads"
PROCESSED_DIR = DATA_DIR / "processed"

DOCUMENTS_DB_PATH = DATA_DIR / "documents.json"

JSON_ENCODING = "utf-8"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def load_documents() -> dict[str, Any]:
    """
    Load document metadata from the JSON storage file.

    Returns:
        Dictionary containing all stored document metadata.
    """
    if not DOCUMENTS_DB_PATH.exists():
        return {}

    with open(DOCUMENTS_DB_PATH, "r", encoding=JSON_ENCODING) as file:
        return json.load(file)


def save_documents(documents: dict[str, Any]) -> None:
    """
    Persist document metadata to disk.

    Args:
        documents: Metadata dictionary to save.
    """
    with open(DOCUMENTS_DB_PATH, "w", encoding=JSON_ENCODING) as file:
        json.dump(
            documents,
            file,
            ensure_ascii=False,
            indent=2,
        )


def save_document_metadata(
    document_id: str,
    metadata: dict[str, Any],
) -> None:
    """
    Save metadata for a new document.

    Args:
        document_id: Unique document identifier.
        metadata: Document metadata.
    """
    documents = load_documents()

    documents[document_id] = metadata

    save_documents(documents)


def get_document_metadata(
    document_id: str,
) -> dict[str, Any] | None:
    """
    Retrieve metadata for a specific document.

    Args:
        document_id: Unique document identifier.

    Returns:
        Document metadata or None if not found.
    """
    documents = load_documents()

    return documents.get(document_id)


def update_document_metadata(
    document_id: str,
    updates: dict[str, Any],
) -> None:
    """
    Update existing document metadata.

    Args:
        document_id: Unique document identifier.
        updates: Fields to update.
    """
    documents = load_documents()

    if document_id not in documents:
        return

    documents[document_id].update(updates)

    save_documents(documents)