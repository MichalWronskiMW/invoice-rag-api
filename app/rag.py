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


def split_text_into_chunks(
    text: str,
    chunk_size: int = 300,
    overlap: int = 50,
) -> list[str]:
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


def search_documents(
    query: str,
    top_k: int = 3,
    document_id: str | None = None,
):
    where_filter = None

    if document_id:
        where_filter = {
            "document_id": document_id
        }

    results = collection.query(
        query_texts=[query],
        n_results=top_k,
        where=where_filter,
    )

    output = []

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

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
    top_k: int = 3,
    document_id: str | None = None,
):
    results = search_documents(
        query=query,
        top_k=top_k,
        document_id=document_id,
    )

    sources = [
        item["chunk_text"]
        for item in results
    ]

    if not sources:
        return {
            "answer": "No relevant documents found.",
            "sources": [],
        }

    answer = (
        "Based on the retrieved document fragments:\n\n"
        + "\n\n---\n\n".join(sources)
    )

    return {
        "answer": answer,
        "sources": sources,
    }