from pathlib import Path
import uuid

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, status

from app.ocr import extract_text
from app.rag import (
    index_document,
    search_documents,
    answer_question,
)
from fastapi import FastAPI, UploadFile, File, HTTPException

from app.schemas import (
    UploadResponse,
    DocumentResponse,
    IndexResponse,
    SearchRequest,
    SearchResponse,
    AnswerRequest,
    AnswerResponse,
)

from app.storage import (
    UPLOAD_DIR,
    save_document_metadata,
    get_document_metadata,
    update_document_metadata,
)
app = FastAPI(
    title="Invoice OCR RAG API",
    version="0.1.0",
)

def process_document_ocr(document_id: str, image_path: str) -> None:
    try:
        update_document_metadata(
            document_id,
            {"status": "processing"}
        )

        text = extract_text(image_path)

        update_document_metadata(
            document_id,
            {
                "status": "completed",
                "text": text,
                "error": None,
            }
        )

    except Exception as e:
        update_document_metadata(
            document_id,
            {
                "status": "failed",
                "error": str(e),
            }
        )

@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post(
    "/documents/upload",
    response_model=UploadResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Upload document",
    description="Uploads invoice image and starts OCR processing.",
)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    allowed_extensions = {".jpg", ".jpeg", ".png"}
    extension = Path(file.filename).suffix.lower()

    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Only jpg, jpeg and png files are allowed.",
        )

    document_id = str(uuid.uuid4())
    save_path = UPLOAD_DIR / f"{document_id}{extension}"

    content = await file.read()

    with open(save_path, "wb") as f:
        f.write(content)

    metadata = {
        "document_id": document_id,
        "status": "queued",
        "filename": file.filename,
        "saved_path": str(save_path),
        "text": None,
        "error": None,
    }

    save_document_metadata(document_id, metadata)

    background_tasks.add_task(
        process_document_ocr,
        document_id,
        str(save_path),
    )

    return UploadResponse(document_id=document_id, status="queued")


@app.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: str):
    metadata = get_document_metadata(document_id)

    if metadata is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    if metadata.get("status") == "failed":
        raise HTTPException(
            status_code=500,
            detail=metadata.get("error", "OCR processing failed."),
        )

    return metadata


@app.post("/documents/{document_id}/index", response_model=IndexResponse)
async def index_document_endpoint(document_id: str):
    metadata = get_document_metadata(document_id)

    if metadata is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    if metadata["status"] != "completed":
        raise HTTPException(
            status_code=409,
            detail="Document is not processed yet.",
        )

    text = metadata.get("text")

    if not text:
        raise HTTPException(
            status_code=409,
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
)
async def rag_search(
    request: SearchRequest,
):
    results = search_documents(
        query=request.query,
        top_k=request.top_k,
        document_id=request.document_id,
    )

    return SearchResponse(
        results=results
    )


@app.post(
    "/rag/answer",
    response_model=AnswerResponse,
)
async def rag_answer(
    request: AnswerRequest,
):
    result = answer_question(
        query=request.query,
        top_k=request.top_k,
        document_id=request.document_id,
    )

    return AnswerResponse(
        answer=result["answer"],
        model="mistral:latest",
        sources=result["sources"],
    )