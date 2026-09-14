import math
from dataclasses import dataclass

from app.models import SearchMethod
from app.rag.retriever import InMemoryHybridRetriever


@dataclass(frozen=True)
class BenchmarkQuestion:
    question_id: str
    query: str
    relevant_chunk_ids: set[str]
    category: str = "unspecified"


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


def run_detailed_benchmark(
    retriever: InMemoryHybridRetriever,
    questions: list[BenchmarkQuestion],
    *,
    methods: list[SearchMethod],
    k_values: tuple[int, ...] = (1, 3, 5),
) -> tuple[dict[str, dict[str, float]], list[dict[str, object]]]:
    """Return multi-k summary metrics and inspectable ranks for every question."""
    if not questions:
        raise ValueError("Benchmark requires at least one question")
    if not k_values or any(k <= 0 for k in k_values):
        raise ValueError("k values must be greater than zero")

    max_k = max(k_values)
    summary: dict[str, dict[str, float]] = {}
    details: list[dict[str, object]] = []

    for method in methods:
        metric_rows: dict[int, list[RetrievalMetrics]] = {k: [] for k in k_values}
        for question in questions:
            results = retriever.search(question.query, limit=max_k, method=method)
            retrieved_ids = [result.chunk_id for result in results]
            gold_rank = next(
                (
                    rank
                    for rank, chunk_id in enumerate(retrieved_ids, start=1)
                    if chunk_id in question.relevant_chunk_ids
                ),
                None,
            )
            details.append(
                {
                    "question_id": question.question_id,
                    "category": question.category,
                    "query": question.query,
                    "method": method.value,
                    "gold_chunk_ids": sorted(question.relevant_chunk_ids),
                    "gold_rank": gold_rank,
                    "top_chunk_id": retrieved_ids[0] if retrieved_ids else None,
                    "retrieved_chunk_ids": retrieved_ids,
                }
            )
            for k in k_values:
                metric_rows[k].append(
                    evaluate_ranking(retrieved_ids, question.relevant_chunk_ids, k=k)
                )

        count = len(questions)
        method_summary: dict[str, float] = {"questions": float(count)}
        for k in k_values:
            scores = metric_rows[k]
            method_summary[f"precision@{k}"] = (
                sum(value.precision_at_k for value in scores) / count
            )
            method_summary[f"recall@{k}"] = sum(value.recall_at_k for value in scores) / count
            method_summary[f"mrr@{k}"] = sum(value.reciprocal_rank for value in scores) / count
            method_summary[f"ndcg@{k}"] = sum(value.ndcg_at_k for value in scores) / count
        summary[method.value] = method_summary

    return summary, details
