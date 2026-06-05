from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions

CHROMA_DIR = Path("data/vector_store/chroma_db")
COLLECTION_NAME = "invoice_documents"

CHROMA_DIR.mkdir(parents=True, exist_ok=True)

embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

client = chromadb.PersistentClient(path=str(CHROMA_DIR))

collection = client.get_or_create_collection(
    name=COLLECTION_NAME,
    embedding_function=embedding_function,
)


def split_text_into_chunks(text: str, chunk_size: int = 700, overlap: int = 100) -> list[str]:
    if not text:
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


def index_document(document_id: str, text: str) -> int:
    chunks = split_text_into_chunks(text)

    if not chunks:
        return 0

    ids = [
        f"{document_id}_chunk_{i}"
        for i in range(len(chunks))
    ]

    metadatas = [
        {
            "document_id": document_id,
            "chunk_index": i,
        }
        for i in range(len(chunks))
    ]

    collection.upsert(
        ids=ids,
        documents=chunks,
        metadatas=metadatas,
    )

    return len(chunks)