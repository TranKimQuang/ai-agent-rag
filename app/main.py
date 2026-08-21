from pathlib import Path
from uuid import uuid4

from fastapi import Body, FastAPI, Header, HTTPException, Query

from app.models import IngestResponse, SearchResponse
from app.rag.chunking import chunk_pages
from app.rag.pdf_reader import PdfReadError, extract_pdf_pages
from app.rag.retriever import InMemoryBM25Retriever

app = FastAPI(title="AI Agent + RAG")
retriever = InMemoryBM25Retriever()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/documents", response_model=IngestResponse, status_code=201)
async def ingest_document(
    content: bytes = Body(media_type="application/pdf"),
    x_filename: str = Header(default="document.pdf"),
) -> IngestResponse:
    filename = Path(x_filename).name
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

    retriever.add(chunks)
    return IngestResponse(
        document_id=document_id,
        filename=filename,
        pages=len(pages),
        chunks=len(chunks),
    )


@app.get("/search", response_model=SearchResponse)
def search(
    q: str = Query(min_length=2, description="Question or keywords to search for"),
    limit: int = Query(default=5, ge=1, le=20),
) -> SearchResponse:
    return SearchResponse(query=q, results=retriever.search(q, limit))
