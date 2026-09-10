from enum import Enum

from pydantic import BaseModel, Field


class SearchMethod(str, Enum):
    BM25 = "bm25"
    SEMANTIC = "semantic"
    HYBRID = "hybrid"
    HYBRID_ONTOLOGY = "hybrid_ontology"


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
    ontology_score: float | None = Field(default=None, ge=0, le=1)
    query_concepts: list[str] = Field(default_factory=list)
    chunk_concepts: list[str] = Field(default_factory=list)
    expanded_query: str | None = None
    ontology_explanation: str | None = None


class SearchResponse(BaseModel):
    query: str
    method: SearchMethod
    results: list[SearchResult]


class OntologySummary(BaseModel):
    classes: int
    object_properties: int
    data_properties: int
    individuals: int


class OntologyRelation(BaseModel):
    subject: str
    predicate: str
    object: str


class OntologyQueryResponse(BaseModel):
    concept: str
    relations: list[OntologyRelation]


class OntologyExpansionResponse(BaseModel):
    original_query: str
    expanded_query: str
    query_concepts: list[str]
    expansion_terms: list[str]
