import json
from pathlib import Path

from app.models import SearchMethod
from app.ontology.service import OntologyService
from app.rag.chunking import chunk_pages
from app.rag.pdf_reader import extract_pdf_pages
from app.rag.retriever import InMemoryHybridRetriever

PROJECT_ROOT = Path(__file__).parents[1]
PDF_PATH = PROJECT_ROOT / "output" / "pdf" / "tai-lieu-kiem-thu-ontology-rag.pdf"
DATASET_PATH = PROJECT_ROOT / "evaluation" / "pdf_benchmark.json"


def test_generated_pdf_runs_through_real_ingestion_pipeline() -> None:
    pages = extract_pdf_pages(PDF_PATH.read_bytes())
    chunks = chunk_pages(
        pages,
        document_id="ontology-rag-test",
        filename=PDF_PATH.name,
    )
    ontology = OntologyService()
    chunks, concept_links = ontology.index_chunks(chunks)

    assert len(pages) == 8
    assert len(chunks) == 8
    assert concept_links >= 20
    assert "KeywordSearch" in chunks[0].concepts
    assert "HybridSearch" in chunks[2].concepts
    assert "RetrievalAugmentedGeneration" in chunks[3].concepts


def test_generated_pdf_bm25_finds_expected_gold_chunk() -> None:
    payload = json.loads(DATASET_PATH.read_text(encoding="utf-8"))
    pages = extract_pdf_pages(PDF_PATH.read_bytes())
    chunks = chunk_pages(
        pages,
        document_id="ontology-rag-test",
        filename=PDF_PATH.name,
    )
    retriever = InMemoryHybridRetriever()
    retriever.add(chunks)

    question = payload["questions"][0]
    results = retriever.search(question["query"], method=SearchMethod.BM25)

    assert results[0].chunk_id in question["relevant_chunk_ids"]
    assert results[0].page == 1
