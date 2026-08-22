from enum import Enum

from pydantic import BaseModel, Field


class SearchMethod(str, Enum):
    BM25 = "bm25"
    SEMANTIC = "semantic"
    HYBRID = "hybrid"


class Chunk(BaseModel):
    id: str
    document_id: str
    filename: str
    page: int
    text: str


class IngestResponse(BaseModel):
    document_id: str
    filename: str
    pages: int
    chunks: int


class SearchResult(BaseModel):
    chunk_id: str
    document_id: str
    filename: str
    page: int
    text: str
    method: SearchMethod
    score: float = Field(ge=0)
    bm25_score: float | None = Field(default=None, ge=0)
    semantic_score: float | None = Field(default=None, ge=0, le=1)


class SearchResponse(BaseModel):
    query: str
    method: SearchMethod
    results: list[SearchResult]
