import numpy as np

from app.evaluation.benchmark import (
    BenchmarkQuestion,
    evaluate_ranking,
    run_benchmark,
    run_detailed_benchmark,
)
from app.models import Chunk, SearchMethod
from app.ontology.service import OntologyService
from app.rag.retriever import InMemoryHybridRetriever


class BenchmarkEncoder:
    def encode(self, texts: list[str]) -> np.ndarray:
        vectors = []
        for text in texts:
            lowered = text.lower()
            if "bm25" in lowered or "keyword" in lowered:
                vectors.append([1.0, 0.0])
            else:
                vectors.append([0.0, 1.0])
        return np.asarray(vectors, dtype=np.float32)


def test_evaluate_ranking_calculates_standard_metrics() -> None:
    metrics = evaluate_ranking(["wrong", "correct"], {"correct"}, k=2)

    assert metrics.precision_at_k == 0.5
    assert metrics.recall_at_k == 1.0
    assert metrics.reciprocal_rank == 0.5
    assert 0.0 < metrics.ndcg_at_k < 1.0


def test_run_benchmark_compares_retrieval_methods() -> None:
    ontology = OntologyService()
    chunks, _ = ontology.index_chunks(
        [
            Chunk(
                id="bm25",
                document_id="doc",
                filename="paper.pdf",
                page=1,
                text="BM25 performs keyword search.",
            ),
            Chunk(
                id="semantic",
                document_id="doc",
                filename="paper.pdf",
                page=2,
                text="Semantic search uses embeddings.",
            ),
        ]
    )
    retriever = InMemoryHybridRetriever(
        semantic_encoder=BenchmarkEncoder(),
        ontology_service=ontology,
    )
    retriever.add(chunks)

    report = run_benchmark(
        retriever,
        [BenchmarkQuestion("q1", "BM25 keyword", {"bm25"})],
        methods=[SearchMethod.BM25, SearchMethod.HYBRID_ONTOLOGY],
        k=1,
    )

    assert report["bm25"]["recall@1"] == 1.0
    assert report["hybrid_ontology"]["mrr"] == 1.0


def test_detailed_benchmark_reports_each_question_rank_and_multiple_k_values() -> None:
    ontology = OntologyService()
    chunks, _ = ontology.index_chunks(
        [
            Chunk(id="wrong", document_id="doc", filename="paper.pdf", page=1, text="Other"),
            Chunk(
                id="correct",
                document_id="doc",
                filename="paper.pdf",
                page=2,
                text="BM25 performs keyword search.",
            ),
        ]
    )
    retriever = InMemoryHybridRetriever(
        semantic_encoder=BenchmarkEncoder(), ontology_service=ontology
    )
    retriever.add(chunks)

    summary, details = run_detailed_benchmark(
        retriever,
        [BenchmarkQuestion("q1", "BM25 keyword", {"correct"}, "keyword")],
        methods=[SearchMethod.BM25],
        k_values=(1, 3),
    )

    assert summary["bm25"]["recall@1"] == 1.0
    assert summary["bm25"]["recall@3"] == 1.0
    assert details[0]["gold_rank"] == 1
    assert details[0]["category"] == "keyword"
