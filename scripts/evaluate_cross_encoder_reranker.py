"""Evaluate an optional cross-encoder reranker on QASPER development cases."""

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

from app.models import Chunk, ConceptLinkingMethod, SearchMethod, SearchResult
from app.ontology.service import OntologyService
from app.rag.retriever import InMemoryHybridRetriever, SentenceTransformerEncoder


def find_gold_rank(results: list[SearchResult], gold_ids: set[str]) -> int | None:
    return next(
        (
            rank
            for rank, result in enumerate(results, start=1)
            if result.chunk_id in gold_ids
        ),
        None,
    )


def rerank_with_scores(
    candidates: list[SearchResult], scores: list[float]
) -> list[SearchResult]:
    if len(candidates) != len(scores):
        raise ValueError("Candidates and scores must have the same length")
    paired = zip(candidates, scores, strict=True)
    return [
        candidate.model_copy(update={"score": float(score)})
        for candidate, score in sorted(paired, key=lambda item: item[1], reverse=True)
    ]


def reciprocal_rank(rank: int | None) -> float:
    return 0.0 if rank is None else 1.0 / rank


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("results/qasper_answer_evaluation_20260927T115655Z.json"),
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        default=Path("evaluation/qasper_train_v3/qasper_train_development.json"),
    )
    parser.add_argument(
        "--model", default="cross-encoder/ms-marco-MiniLM-L6-v2"
    )
    parser.add_argument("--device", default=None)
    parser.add_argument("--candidate-limit", type=int, default=20)
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument(
        "--output", type=Path, default=Path("results/qasper_cross_encoder_reranker.json")
    )
    args = parser.parse_args()

    run = json.loads(args.input.read_text(encoding="utf-8"))
    dataset = json.loads(args.dataset.read_text(encoding="utf-8"))
    if "heldout" in str(dataset.get("metadata", {}).get("split", "")).lower():
        raise ValueError("Cross-encoder development evaluation must not use held-out data")

    encoder = SentenceTransformerEncoder()
    ontology = OntologyService(
        semantic_encoder=encoder,
        linking_method=ConceptLinkingMethod.HYBRID,
        linking_threshold=0.65,
    )
    chunks = [Chunk.model_validate(item) for item in dataset["chunks"]]
    chunks, concept_links = ontology.index_chunks(chunks)
    retriever = InMemoryHybridRetriever(
        semantic_encoder=encoder,
        ontology_service=ontology,
    )
    retriever.add(chunks)

    from sentence_transformers import CrossEncoder

    cross_encoder = CrossEncoder(args.model, device=args.device)
    rows: list[dict[str, object]] = []
    for row in run["cases"]:
        if row["expected_kind"] != "answerable":
            continue
        query = str(row["question"])
        gold_ids = {
            str(chunk_id)
            for reference in row["references"]
            for chunk_id in reference["evidence_chunk_ids"]
        }
        candidates = retriever.search(
            query,
            args.candidate_limit,
            SearchMethod.HYBRID_ONTOLOGY_RERANK,
            str(row["paper_id"]),
        )
        scores = cross_encoder.predict(
            [(query, candidate.text) for candidate in candidates],
            show_progress_bar=False,
        ).tolist()
        reranked = rerank_with_scores(candidates, scores)
        rows.append(
            {
                "question_id": row["question_id"],
                "question": query,
                "candidate_gold_rank": find_gold_rank(candidates, gold_ids),
                "reranked_gold_rank": find_gold_rank(reranked, gold_ids),
                "reranked_chunk_ids": [item.chunk_id for item in reranked[: args.limit]],
            }
        )

    baseline_hits = sum(
        row["candidate_gold_rank"] is not None
        and int(row["candidate_gold_rank"]) <= args.limit
        for row in rows
    )
    reranked_hits = sum(
        row["reranked_gold_rank"] is not None
        and int(row["reranked_gold_rank"]) <= args.limit
        for row in rows
    )
    summary = {
        "questions": len(rows),
        "candidate_limit": args.candidate_limit,
        "limit": args.limit,
        "candidate_recall": sum(row["candidate_gold_rank"] is not None for row in rows)
        / len(rows),
        "baseline_recall_at_k": baseline_hits / len(rows),
        "reranked_recall_at_k": reranked_hits / len(rows),
        "baseline_mrr": sum(
            reciprocal_rank(row["candidate_gold_rank"]) for row in rows
        )
        / len(rows),
        "reranked_mrr": sum(reciprocal_rank(row["reranked_gold_rank"]) for row in rows)
        / len(rows),
    }
    report = {
        "metadata": {
            "created_at": datetime.now(UTC).isoformat(),
            "dataset": str(args.dataset),
            "input": str(args.input),
            "model": args.model,
            "device": args.device,
            "heldout_used": False,
            "concept_links": concept_links,
        },
        "summary": summary,
        "cases": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2), flush=True)
    print(f"Saved: {args.output}", flush=True)


if __name__ == "__main__":
    main()
