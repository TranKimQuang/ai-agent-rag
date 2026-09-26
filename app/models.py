from enum import Enum

from pydantic import BaseModel, Field


class SearchMethod(str, Enum):
    BM25 = "bm25"
    SEMANTIC = "semantic"
    HYBRID = "hybrid"
    HYBRID_ONTOLOGY_EXPANSION = "hybrid_ontology_expansion"
    HYBRID_ONTOLOGY_RERANK = "hybrid_ontology_rerank"
    HYBRID_ONTOLOGY = "hybrid_ontology"


class AgentStatus(str, Enum):
    ANSWERED = "answered"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"


class ConceptLinkingMethod(str, Enum):
    ALIAS = "alias"
    SEMANTIC = "semantic"
    HYBRID = "hybrid"


class Chunk(BaseModel):
    id: str
    document_id: str
    filename: str
    page: int
    text: str
    concepts: list[str] = Field(default_factory=list)


class IngestResponse(BaseModel):
    document_id: str
    filename: str
    pages: int
    chunks: int
    concept_links: int = 0


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


class ConceptLink(BaseModel):
    concept: str
    label: str
    score: float = Field(ge=0, le=1)
    source: ConceptLinkingMethod


class ConceptLinkingResponse(BaseModel):
    text: str
    method: ConceptLinkingMethod
    threshold: float = Field(ge=0, le=1)
    links: list[ConceptLink]


class AskRequest(BaseModel):
    question: str = Field(min_length=2)
    limit: int = Field(default=5, ge=1, le=10)
    document_id: str | None = Field(
        default=None,
        min_length=1,
        description="Optional document scope for questions about a specific PDF or paper.",
    )


class Citation(BaseModel):
    filename: str
    page: int = Field(ge=1)
    chunk_id: str
    quote: str


class AgentStep(BaseModel):
    name: str
    status: str
    detail: str


class AskResponse(BaseModel):
    question: str
    status: AgentStatus
    answer: str
    confidence: float = Field(ge=0, le=1)
    citations: list[Citation] = Field(default_factory=list)
    query_concepts: list[str] = Field(default_factory=list)
    expanded_query: str | None = None
    trace: list[AgentStep] = Field(default_factory=list)
