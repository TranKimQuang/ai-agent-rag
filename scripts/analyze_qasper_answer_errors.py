"""Separate QASPER answer failures into retrieval, gate, answer and citation errors."""

import argparse
import json
from collections import Counter
from pathlib import Path

from app.models import Chunk, ConceptLinkingMethod, SearchMethod, SearchResult
from app.ontology.service import OntologyService
from app.rag.retriever import InMemoryHybridRetriever, SentenceTransformerEncoder


def classify_case(
    row: dict[str, object], retrieved: list[SearchResult]
) -> tuple[str, int | None]:
    if row["expected_kind"] == "unanswerable":
        if row["agent_status"] == "insufficient_evidence":
            return "correct_unanswerable_refusal", None
        return "unsafe_unanswerable_answer", None

    gold_ids = {
        str(chunk_id)
        for reference in row["references"]
        for chunk_id in reference["evidence_chunk_ids"]
    }
    gold_rank = next(
        (
            rank
            for rank, result in enumerate(retrieved, start=1)
            if result.chunk_id in gold_ids
        ),
        None,
    )
    answered = row["agent_status"] == "answered"
    if gold_rank is None:
        return (
            "retrieval_miss_with_answer" if answered else "retrieval_miss_refused",
            None,
        )
    if gold_rank > 3:
        return (
            "context_cutoff_with_answer" if answered else "context_cutoff_refused",
            gold_rank,
        )
    if not answered:
        return "gate_false_rejection", gold_rank
    if float(row["evidence_f1"]) == 0.0:
        return "citation_selection_error", gold_rank
    if float(row["answer_f1"]) < 0.5:
        return "answer_content_or_format_error", gold_rank
    return "successful_answer", gold_rank


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze a saved QASPER answer run")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument(
        "--dataset",
        type=Path,
        default=Path("evaluation/qasper_train_v3/qasper_train_development.json"),
    )
    parser.add_argument(
        "--output", type=Path, default=Path("results/qasper_answer_error_analysis.json")
    )
    args = parser.parse_args()
    run = json.loads(args.input.read_text(encoding="utf-8"))
    dataset = json.loads(args.dataset.read_text(encoding="utf-8"))
    if "heldout" in str(dataset.get("metadata", {}).get("split", "")).lower():
        raise ValueError("Development error analysis must not use held-out data")

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

    details = []
    categories: Counter[str] = Counter()
    for row in run["cases"]:
        retrieved = retriever.search(
            str(row["question"]),
            5,
            SearchMethod.HYBRID_ONTOLOGY_RERANK,
            str(row["paper_id"]),
        )
        category, gold_rank = classify_case(row, retrieved)
        categories[category] += 1
        details.append(
            {
                "question_id": row["question_id"],
                "paper_id": row["paper_id"],
                "question": row["question"],
                "expected_kind": row["expected_kind"],
                "agent_status": row["agent_status"],
                "category": category,
                "gold_rank": gold_rank,
                "answer_f1": row["answer_f1"],
                "evidence_f1": row["evidence_f1"],
                "retrieved_chunk_ids": [result.chunk_id for result in retrieved],
                "citation_chunk_ids": row["citation_chunk_ids"],
            }
        )
    report = {
        "input": str(args.input),
        "dataset": str(args.dataset),
        "heldout_used": False,
        "concept_links": concept_links,
        "categories": dict(sorted(categories.items())),
        "details": details,
        "notes": {
            "model_context": "top 3 of the top-5 retrieval results",
            "success_threshold": "gold citation overlap and Answer-F1 >= 0.5",
            "warning": "QASPER gold evidence can be incomplete; categories are diagnostic proxies.",
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report["categories"], indent=2), flush=True)
    print(f"Saved: {args.output}", flush=True)


if __name__ == "__main__":
    main()
