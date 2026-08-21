from pydantic import BaseModel, Field


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
    score: float = Field(ge=0)


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]

