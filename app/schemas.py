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


class SearchRequest(BaseModel):
    query: str
    top_k: int = 3


class SearchResult(BaseModel):
    document_id: str
    chunk_text: str


class SearchResponse(BaseModel):
    results: list[SearchResult]


class AnswerRequest(BaseModel):
    query: str
    top_k: int = 3


class AnswerResponse(BaseModel):
    answer: str
    sources: list[str]