from pydantic import BaseModel


class UploadResponse(BaseModel):
    document_id: str
    status: str


class DocumentResponse(BaseModel):
    document_id: str
    status: str
    filename: str
    saved_path: str
    text: str | None = None
    error: str | None = None


class IndexResponse(BaseModel):
    document_id: str
    status: str
    chunks_indexed: int