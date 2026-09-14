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

    assert len(pages) == 16
    assert len(chunks) == 16
    assert concept_links >= 35
    assert "KeywordSearch" in chunks[0].concepts
    assert "HybridSearch" in chunks[2].concepts
    assert "RetrievalAugmentedGeneration" in chunks[3].concepts


def test_generated_benchmark_contains_harder_question_categories() -> None:
    payload = json.loads(DATASET_PATH.read_text(encoding="utf-8"))
    categories = {question["category"] for question in payload["questions"]}

    assert len(payload["chunks"]) == 16
    assert len(payload["questions"]) == 24
    assert {"keyword", "semantic", "indirect", "reasoning", "ontology"} <= categories


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

    assert any(
        result.chunk_id in question["relevant_chunk_ids"] for result in results[:5]
    )
