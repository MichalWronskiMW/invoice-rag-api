from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    """Response returned after uploading a document."""

    document_id: str
    status: str


class DocumentResponse(BaseModel):
    """Document metadata and OCR processing result."""

    document_id: str
    status: str
    filename: str
    saved_path: str

    text: str | None = None
    error: str | None = None

    indexed: bool | None = None
    chunks_indexed: int | None = None


class IndexResponse(BaseModel):
    """Response returned after semantic indexing."""

    document_id: str
    status: str
    chunks_indexed: int


class SearchRequest(BaseModel):
    """Semantic search request."""

    query: str
    top_k: int = Field(default=3, ge=1, le=20)
    document_id: str | None = None


class SearchResult(BaseModel):
    """Single retrieved document chunk."""

    document_id: str
    chunk_text: str


class SearchResponse(BaseModel):
    """Semantic search response."""

    results: list[SearchResult]


class AnswerRequest(BaseModel):
    """RAG question answering request."""

    query: str
    top_k: int = Field(default=3, ge=1, le=20)
    document_id: str | None = None


class AnswerResponse(BaseModel):
    """RAG answer with supporting sources."""

    answer: str
    model: str
    sources: list[str]