from pathlib import Path
import uuid

from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile, status

from app.ocr import extract_text
from app.rag import answer_question, index_document, search_documents
from app.schemas import (
    AnswerRequest,
    AnswerResponse,
    DocumentResponse,
    IndexResponse,
    SearchRequest,
    SearchResponse,
    UploadResponse,
)
from app.storage import (
    UPLOAD_DIR,
    get_document_metadata,
    save_document_metadata,
    update_document_metadata,
)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
LLM_MODEL_NAME = "mistral:latest"

app = FastAPI(
    title="Invoice OCR RAG API",
    description="API for OCR processing, semantic indexing and RAG-based invoice question answering. Prepared by Michał Wroński.",
    version="1.0.0",
)


def process_document_ocr(document_id: str, image_path: str) -> None:
    """Run OCR processing in the background and update document metadata."""
    try:
        update_document_metadata(document_id, {"status": "processing"})

        text = extract_text(image_path)

        update_document_metadata(
            document_id,
            {
                "status": "completed",
                "text": text,
                "error": None,
            },
        )

    except Exception as exc:
        update_document_metadata(
            document_id,
            {
                "status": "failed",
                "error": str(exc),
            },
        )


@app.get(
    "/health",
    summary="Health check",
    description="Checks whether the API is running.",
)
async def health() -> dict[str, str]:
    """Return basic API health status."""
    return {"status": "ok"}


@app.post(
    "/documents/upload",
    response_model=UploadResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Upload document",
    description="Uploads an invoice image and starts OCR processing in the background.",
)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
) -> UploadResponse:
    """Upload an image file and start asynchronous OCR processing."""
    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only jpg, jpeg and png files are allowed.",
        )

    document_id = str(uuid.uuid4())
    save_path = UPLOAD_DIR / f"{document_id}{extension}"

    content = await file.read()

    with open(save_path, "wb") as file_buffer:
        file_buffer.write(content)

    metadata = {
        "document_id": document_id,
        "status": "queued",
        "filename": file.filename,
        "saved_path": str(save_path),
        "text": None,
        "error": None,
        "indexed": False,
        "chunks_indexed": 0,
    }

    save_document_metadata(document_id, metadata)

    background_tasks.add_task(
        process_document_ocr,
        document_id,
        str(save_path),
    )

    return UploadResponse(
        document_id=document_id,
        status="queued",
    )


@app.get(
    "/documents/{document_id}",
    response_model=DocumentResponse,
    summary="Get document",
    description="Returns document status, OCR text and processing metadata.",
)
async def get_document(document_id: str) -> DocumentResponse:
    """Return metadata and OCR result for a selected document."""
    metadata = get_document_metadata(document_id)

    if metadata is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    if metadata.get("status") == "failed":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=metadata.get("error", "OCR processing failed."),
        )

    return DocumentResponse(**metadata)


@app.post(
    "/documents/{document_id}/index",
    response_model=IndexResponse,
    summary="Index document",
    description="Splits OCR text into chunks, creates embeddings and stores them in ChromaDB.",
)
async def index_document_endpoint(document_id: str) -> IndexResponse:
    """Index processed document text in the vector database."""
    metadata = get_document_metadata(document_id)

    if metadata is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    if metadata["status"] != "completed":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Document is not processed yet.",
        )

    text = metadata.get("text")

    if not text:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Document has no OCR text to index.",
        )

    chunks_indexed = index_document(
        document_id=document_id,
        text=text,
    )

    update_document_metadata(
        document_id,
        {
            "indexed": True,
            "chunks_indexed": chunks_indexed,
        },
    )

    return IndexResponse(
        document_id=document_id,
        status="indexed",
        chunks_indexed=chunks_indexed,
    )


@app.post(
    "/rag/search",
    response_model=SearchResponse,
    summary="Search documents",
    description="Searches indexed invoice fragments using semantic similarity.",
)
async def rag_search(request: SearchRequest) -> SearchResponse:
    """Search indexed document chunks using semantic retrieval."""
    results = search_documents(
        query=request.query,
        top_k=request.top_k,
        document_id=request.document_id,
    )

    return SearchResponse(results=results)


@app.post(
    "/rag/answer",
    response_model=AnswerResponse,
    summary="Answer question",
    description="Answers a question using retrieved document fragments and a local LLM.",
)
async def rag_answer(request: AnswerRequest) -> AnswerResponse:
    """Answer a user question using the RAG pipeline."""
    result = answer_question(
        query=request.query,
        top_k=request.top_k,
        document_id=request.document_id,
    )

    return AnswerResponse(
        answer=result["answer"],
        model=LLM_MODEL_NAME,
        sources=result["sources"],
    )