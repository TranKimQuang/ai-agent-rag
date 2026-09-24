from pathlib import Path
from urllib.parse import unquote
from uuid import uuid4

from fastapi import Body, FastAPI, Header, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.agent.service import DocumentQuestionAgent
from app.models import (
    AskRequest,
    AskResponse,
    ConceptLinkingMethod,
    ConceptLinkingResponse,
    IngestResponse,
    OntologyExpansionResponse,
    OntologyQueryResponse,
    OntologySummary,
    SearchMethod,
    SearchResponse,
)
from app.ontology.service import OntologyService
from app.rag.chunking import chunk_pages
from app.rag.pdf_reader import PdfReadError, extract_pdf_pages
from app.rag.retriever import (
    InMemoryHybridRetriever,
    SemanticModelError,
    SentenceTransformerEncoder,
)

embedding_encoder = SentenceTransformerEncoder()
ontology = OntologyService(
    semantic_encoder=embedding_encoder,
    linking_method=ConceptLinkingMethod.HYBRID,
    linking_threshold=0.60,
)
app = FastAPI(title="AI Agent + RAG")
retriever = InMemoryHybridRetriever(
    semantic_encoder=embedding_encoder,
    ontology_service=ontology,
)
question_agent = DocumentQuestionAgent(retriever)
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/", include_in_schema=False)
def user_interface() -> FileResponse:
    return FileResponse(static_dir / "index.html")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/documents", response_model=IngestResponse, status_code=201)
async def ingest_document(
    content: bytes = Body(media_type="application/pdf"),
    x_filename: str = Header(default="document.pdf"),
) -> IngestResponse:
    filename = Path(unquote(x_filename)).name
    if Path(filename).suffix.lower() != ".pdf":
        raise HTTPException(status_code=415, detail="Only PDF files are supported")

    try:
        pages = extract_pdf_pages(content)
    except PdfReadError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    document_id = uuid4().hex
    chunks = chunk_pages(pages, document_id=document_id, filename=filename)
    if not chunks:
        raise HTTPException(
            status_code=422,
            detail="The PDF contains no extractable text; it may be a scanned image",
        )

    chunks, concept_links = ontology.index_chunks(chunks)
    retriever.add(chunks)
    return IngestResponse(
        document_id=document_id,
        filename=filename,
        pages=len(pages),
        chunks=len(chunks),
        concept_links=concept_links,
    )


@app.get("/search", response_model=SearchResponse)
def search(
    q: str = Query(min_length=2, description="Question or keywords to search for"),
    limit: int = Query(default=5, ge=1, le=20),
    method: SearchMethod = SearchMethod.HYBRID,
) -> SearchResponse:
    try:
        results = retriever.search(q, limit, method)
    except SemanticModelError as exc:
        raise HTTPException(
            status_code=503,
            detail="Embedding model is unavailable. Check the model download and try again.",
        ) from exc

    return SearchResponse(
        query=q,
        method=method,
        results=results,
    )


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest) -> AskResponse:
    try:
        return question_agent.ask(request.question, request.limit)
    except SemanticModelError as exc:
        raise HTTPException(
            status_code=503,
            detail="Embedding model is unavailable. Check the model download and try again.",
        ) from exc


@app.get("/ontology/summary", response_model=OntologySummary)
def ontology_summary() -> OntologySummary:
    return ontology.summary()


@app.get("/ontology/concepts/{concept}", response_model=OntologyQueryResponse)
def ontology_concept(concept: str) -> OntologyQueryResponse:
    relations = ontology.find_relations(concept)
    if not relations:
        raise HTTPException(status_code=404, detail="Concept not found in ontology")
    return OntologyQueryResponse(concept=concept, relations=relations)


@app.get("/ontology/expand", response_model=OntologyExpansionResponse)
def ontology_expand(
    q: str = Query(min_length=2, description="Question to expand with ontology concepts"),
) -> OntologyExpansionResponse:
    expansion = ontology.expand_query(q)
    return OntologyExpansionResponse(
        original_query=expansion.original_query,
        expanded_query=expansion.expanded_query,
        query_concepts=expansion.query_concepts,
        expansion_terms=expansion.expansion_terms,
    )


@app.get("/ontology/concept-linking", response_model=ConceptLinkingResponse)
def ontology_link(
    q: str = Query(min_length=2, description="Text to link to ontology concepts"),
    method: ConceptLinkingMethod = ConceptLinkingMethod.HYBRID,
    threshold: float = Query(default=0.40, ge=0, le=1),
    limit: int = Query(default=5, ge=1, le=20),
) -> ConceptLinkingResponse:
    try:
        links = ontology.link_concepts(
            q,
            method,
            threshold=threshold,
            limit=limit,
        )
    except SemanticModelError as exc:
        raise HTTPException(
            status_code=503,
            detail="Embedding model is unavailable. Check the model download and try again.",
        ) from exc
    return ConceptLinkingResponse(
        text=q,
        method=method,
        threshold=threshold,
        links=links,
    )
