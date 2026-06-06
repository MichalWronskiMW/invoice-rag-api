from pathlib import Path
from typing import Any

import chromadb
from chromadb.utils import embedding_functions

from app.llm import generate_answer_with_ollama

CHROMA_DIR = Path("data/vector_store/chroma_db")
COLLECTION_NAME = "invoice_documents"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

DEFAULT_CHUNK_SIZE = 300
DEFAULT_CHUNK_OVERLAP = 50
DEFAULT_TOP_K = 3

CHROMA_DIR.mkdir(parents=True, exist_ok=True)

embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=EMBEDDING_MODEL_NAME,
)

client = chromadb.PersistentClient(path=str(CHROMA_DIR))

collection = client.get_or_create_collection(
    name=COLLECTION_NAME,
    embedding_function=embedding_function,
)


def split_text_into_chunks(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[str]:
    """
    Split text into overlapping chunks for semantic indexing.

    Args:
        text: Full OCR text extracted from the document.
        chunk_size: Maximum number of characters in a single chunk.
        overlap: Number of overlapping characters between chunks.

    Returns:
        List of text chunks.
    """
    if not text:
        return []

    if chunk_size <= overlap:
        raise ValueError("chunk_size must be greater than overlap.")

    chunks = []
    step = chunk_size - overlap

    for start in range(0, len(text), step):
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

    return chunks


def index_document(document_id: str, text: str) -> int:
    """
    Index a processed document in ChromaDB.

    The document text is split into chunks. Each chunk is embedded
    and stored with metadata containing the original document ID.

    Args:
        document_id: Unique document identifier.
        text: OCR text to index.

    Returns:
        Number of indexed chunks.
    """
    chunks = split_text_into_chunks(text)

    if not chunks:
        return 0

    ids = [f"{document_id}_chunk_{index}" for index in range(len(chunks))]

    metadatas = [
        {
            "document_id": document_id,
            "chunk_index": index,
        }
        for index in range(len(chunks))
    ]

    collection.upsert(
        ids=ids,
        documents=chunks,
        metadatas=metadatas,
    )

    return len(chunks)


def search_documents(
    query: str,
    top_k: int = DEFAULT_TOP_K,
    document_id: str | None = None,
) -> list[dict[str, Any]]:
    """
    Search indexed document chunks using semantic similarity.

    Args:
        query: User search query.
        top_k: Number of top chunks to return.
        document_id: Optional document filter.

    Returns:
        List of matching chunks with document metadata.
    """
    if top_k < 1:
        top_k = DEFAULT_TOP_K

    where_filter = None

    if document_id:
        where_filter = {"document_id": document_id}

    results = collection.query(
        query_texts=[query],
        n_results=top_k,
        where=where_filter,
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    output = []

    for document, metadata in zip(documents, metadatas):
        output.append(
            {
                "document_id": metadata["document_id"],
                "chunk_text": document,
            }
        )

    return output


def answer_question(
    query: str,
    top_k: int = DEFAULT_TOP_K,
    document_id: str | None = None,
) -> dict[str, list[str] | str]:
    """
    Answer a question using retrieved document chunks and a local LLM.

    If the LLM is unavailable, the function falls back to returning
    the retrieved context directly.

    Args:
        query: User question.
        top_k: Number of chunks used as context.
        document_id: Optional document filter.

    Returns:
        Dictionary with generated answer and source chunks.
    """
    results = search_documents(
        query=query,
        top_k=top_k,
        document_id=document_id,
    )

    sources = [item["chunk_text"] for item in results]

    if not sources:
        return {
            "answer": "No relevant documents found.",
            "sources": [],
        }

    context = "\n\n---\n\n".join(sources)

    try:
        answer = generate_answer_with_ollama(
            query=query,
            context=context,
        )
    except Exception as exc:
        answer = (
            "LLM generation failed. Returning retrieved context instead.\n\n"
            f"Error: {exc}\n\n"
            f"{context}"
        )

    return {
        "answer": answer,
        "sources": sources,
    }