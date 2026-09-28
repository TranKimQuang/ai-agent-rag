"""Add semantic-similarity diagnostics and a manual review sheet to an answer run."""

import argparse
import csv
import json
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

from app.rag.retriever import SentenceTransformerEncoder


def max_cosine_similarity(
    prediction: NDArray[np.float32],
    references: NDArray[np.float32],
) -> float:
    if references.size == 0:
        return 0.0
    return float(np.max(references @ prediction))


def needs_manual_review(
    *,
    answer_f1: float,
    semantic_similarity: float,
    evidence_f1: float,
    status: str,
) -> bool:
    return (
        abs(semantic_similarity - answer_f1) >= 0.30
        or (evidence_f1 > 0 and answer_f1 < 0.50)
        or (answer_f1 >= 0.50 and evidence_f1 == 0)
        or status == "generation_error"
    )


def load_review_suggestions(path: Path | None) -> dict[str, dict[str, object]]:
    if path is None:
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    suggestions = payload.get("cases", [])
    return {str(case["question_id"]): case for case in suggestions}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument(
        "--dataset",
        type=Path,
        default=Path("evaluation/qasper_train_v3/qasper_train_development.json"),
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=Path("results/qasper_answer_semantic_review.json"),
    )
    parser.add_argument(
        "--output-csv",
        type=Path,
        default=Path("results/qasper_answer_manual_review.csv"),
    )
    parser.add_argument(
        "--review-suggestions",
        type=Path,
        help=(
            "Optional AI-assisted pre-review labels. These are exported separately "
            "and never populate the human-review columns."
        ),
    )
    args = parser.parse_args()

    run = json.loads(args.input.read_text(encoding="utf-8"))
    dataset = json.loads(args.dataset.read_text(encoding="utf-8"))
    if "heldout" in str(dataset.get("metadata", {}).get("split", "")).lower():
        raise ValueError("Answer semantic diagnostics must not use held-out data")
    suggestions = load_review_suggestions(args.review_suggestions)
    chunk_text = {str(chunk["id"]): str(chunk["text"]) for chunk in dataset["chunks"]}

    answerable = [
        row for row in run["cases"] if row["expected_kind"] == "answerable"
    ]
    texts: list[str] = []
    spans: list[tuple[int | None, list[int]]] = []
    for row in answerable:
        prediction = str(row["prediction"]).strip()
        prediction_index = len(texts) if prediction else None
        if prediction:
            texts.append(prediction)
        reference_indices = []
        for reference in row["references"]:
            answer = str(reference["answer"]).strip()
            if answer and answer.lower() != "unanswerable":
                reference_indices.append(len(texts))
                texts.append(answer)
        spans.append((prediction_index, reference_indices))

    encoder = SentenceTransformerEncoder()
    vectors = encoder.encode(texts) if texts else np.empty((0, 0), dtype=np.float32)
    rows = []
    for source, (prediction_index, reference_indices) in zip(
        answerable, spans, strict=True
    ):
        semantic_similarity = 0.0
        if prediction_index is not None and reference_indices:
            semantic_similarity = max_cosine_similarity(
                vectors[prediction_index],
                vectors[reference_indices],
            )
        answer_f1 = float(source["answer_f1"])
        evidence_f1 = float(source["evidence_f1"])
        status = str(source["agent_status"])
        review = needs_manual_review(
            answer_f1=answer_f1,
            semantic_similarity=semantic_similarity,
            evidence_f1=evidence_f1,
            status=status,
        )
        suggestion = suggestions.get(str(source["question_id"]), {})
        rows.append(
            {
                "question_id": source["question_id"],
                "paper_id": source["paper_id"],
                "question": source["question"],
                "prediction": source["prediction"],
                "reference_answers": " || ".join(
                    str(reference["answer"]) for reference in source["references"]
                ),
                "citation_chunk_ids": " || ".join(source["citation_chunk_ids"]),
                "citation_texts": " || ".join(
                    chunk_text.get(str(chunk_id), "[missing chunk]")
                    for chunk_id in source["citation_chunk_ids"]
                ),
                "answer_f1": answer_f1,
                "semantic_similarity": semantic_similarity,
                "evidence_f1": evidence_f1,
                "agent_status": status,
                "needs_manual_review": review,
                "suggested_answer_correct_0_1_2": suggestion.get(
                    "suggested_answer_correct_0_1_2", ""
                ),
                "suggested_citation_supported_0_1": suggestion.get(
                    "suggested_citation_supported_0_1", ""
                ),
                "suggested_notes": suggestion.get("suggested_notes", ""),
                "manual_answer_correct_0_1_2": "",
                "manual_citation_supported_0_1": "",
                "manual_notes": "",
            }
        )

    semantic_values = [float(row["semantic_similarity"]) for row in rows]
    lexical_values = [float(row["answer_f1"]) for row in rows]
    if not rows:
        raise ValueError("Input run contains no answerable cases")
    correlation = (
        float(np.corrcoef(lexical_values, semantic_values)[0, 1])
        if len(rows) > 1
        else 0.0
    )
    summary = {
        "answerable_questions": len(rows),
        "mean_answer_f1": float(np.mean(lexical_values)),
        "mean_semantic_similarity": float(np.mean(semantic_values)),
        "pearson_correlation": correlation,
        "manual_review_cases": sum(bool(row["needs_manual_review"]) for row in rows),
        "suggestions_loaded": sum(
            bool(row["suggested_notes"]) for row in rows
        ),
        "low_f1_high_semantic": sum(
            float(row["answer_f1"]) < 0.50
            and float(row["semantic_similarity"]) >= 0.70
            for row in rows
        ),
        "heldout_used": False,
        "warning": (
            "Embedding similarity is a diagnostic proxy, not factual correctness. "
            "Use the CSV columns for human answer/citation review."
        ),
    }
    report = {
        "input": str(args.input),
        "dataset": str(args.dataset),
        "summary": summary,
        "cases": rows,
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    with args.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps(summary, indent=2), flush=True)
    print(f"Saved: {args.output_json}", flush=True)
    print(f"Saved: {args.output_csv}", flush=True)


if __name__ == "__main__":
    main()
