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
    indexed: bool | None = None
    chunks_indexed: int | None = None

class IndexResponse(BaseModel):
    document_id: str
    status: str
    chunks_indexed: int


class SearchRequest(BaseModel):
    query: str
    top_k: int = 3
    document_id: str | None = None


class SearchResult(BaseModel):
    document_id: str
    chunk_text: str


class SearchResponse(BaseModel):
    results: list[SearchResult]


class AnswerRequest(BaseModel):
    query: str
    top_k: int = 3
    document_id: str | None = None


class AnswerResponse(BaseModel):
    answer: str
    model: str
    sources: list[str]