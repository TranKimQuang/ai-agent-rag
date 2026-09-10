import math
from dataclasses import dataclass

from app.models import SearchMethod
from app.rag.retriever import InMemoryHybridRetriever


@dataclass(frozen=True)
class BenchmarkQuestion:
    question_id: str
    query: str
    relevant_chunk_ids: set[str]


@dataclass(frozen=True)
class RetrievalMetrics:
    precision_at_k: float
    recall_at_k: float
    reciprocal_rank: float
    ndcg_at_k: float


def evaluate_ranking(
    retrieved_ids: list[str],
    relevant_ids: set[str],
    *,
    k: int,
) -> RetrievalMetrics:
    top_k = retrieved_ids[:k]
    relevant_in_top_k = sum(chunk_id in relevant_ids for chunk_id in top_k)
    precision = relevant_in_top_k / k
    recall = relevant_in_top_k / len(relevant_ids) if relevant_ids else 0.0

    reciprocal_rank = 0.0
    for rank, chunk_id in enumerate(top_k, start=1):
        if chunk_id in relevant_ids:
            reciprocal_rank = 1.0 / rank
            break

    dcg = sum(
        1.0 / math.log2(rank + 1)
        for rank, chunk_id in enumerate(top_k, start=1)
        if chunk_id in relevant_ids
    )
    ideal_hits = min(len(relevant_ids), k)
    ideal_dcg = sum(1.0 / math.log2(rank + 1) for rank in range(1, ideal_hits + 1))
    ndcg = dcg / ideal_dcg if ideal_dcg else 0.0

    return RetrievalMetrics(
        precision_at_k=precision,
        recall_at_k=recall,
        reciprocal_rank=reciprocal_rank,
        ndcg_at_k=ndcg,
    )


def run_benchmark(
    retriever: InMemoryHybridRetriever,
    questions: list[BenchmarkQuestion],
    *,
    methods: list[SearchMethod],
    k: int = 5,
) -> dict[str, dict[str, float]]:
    if not questions:
        raise ValueError("Benchmark requires at least one question")
    if k <= 0:
        raise ValueError("k must be greater than zero")

    report: dict[str, dict[str, float]] = {}
    for method in methods:
        scores = []
        for question in questions:
            results = retriever.search(question.query, limit=k, method=method)
            scores.append(
                evaluate_ranking(
                    [result.chunk_id for result in results],
                    question.relevant_chunk_ids,
                    k=k,
                )
            )

        count = len(scores)
        report[method.value] = {
            f"precision@{k}": sum(value.precision_at_k for value in scores) / count,
            f"recall@{k}": sum(value.recall_at_k for value in scores) / count,
            "mrr": sum(value.reciprocal_rank for value in scores) / count,
            f"ndcg@{k}": sum(value.ndcg_at_k for value in scores) / count,
            "questions": float(count),
        }

    return report
