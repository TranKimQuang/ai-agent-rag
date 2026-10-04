import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any

from app.ontology.service import OntologyService
from app.rag.retriever import SentenceTransformerEncoder


def classify_candidate(
    top_score: float, *, acceptance_threshold: float, review_margin: float
) -> str:
    if top_score >= acceptance_threshold:
        return "unexpected_above_threshold"
    if top_score >= acceptance_threshold - review_margin:
        return "near_threshold"
    if top_score >= 0.4:
        return "weak_existing_match"
    return "vocabulary_gap_or_generic_question"


def render_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Development concept candidate audit",
        "",
        (
            "This audit only uses queries from the development split that received no "
            "concept. It does not inspect validation or final-test retrieval results."
        ),
        "",
        "## Summary",
        "",
        f"- Uncovered queries: **{summary['uncovered_queries']}**",
        f"- Near threshold: **{summary['categories'].get('near_threshold', 0)}**",
        f"- Weak existing match: **{summary['categories'].get('weak_existing_match', 0)}**",
        (
            "- Vocabulary gap or generic question: "
            f"**{summary['categories'].get('vocabulary_gap_or_generic_question', 0)}**"
        ),
        (
            "- Unexpected candidate above threshold: "
            f"**{summary['categories'].get('unexpected_above_threshold', 0)}**"
        ),
        "",
        (
            "The categories are triage labels, not automatic gold labels. Candidates "
            "must be accepted or rejected manually before changing the ontology or "
            "threshold."
        ),
        "",
        "## Candidate queue",
        "",
        "| Category | Top score | Top candidate | Query | Gold evidence concepts |",
        "|---|---:|---|---|---|",
    ]
    for row in payload["queries"]:
        top = row["candidates"][0] if row["candidates"] else None
        query = row["query"].replace("|", "\\|")
        gold = ", ".join(row["gold_concepts"]) or "—"
        lines.append(
            f"| {row['category']} | {top['score']:.4f} | {top['concept']} | "
            f"{query} | {gold} |"
        )
    lines.extend(
        [
            "",
            "## Most frequent top candidates",
            "",
            "| Concept | Queries |",
            "|---|---:|",
        ]
    )
    lines.extend(
        f"| {concept} | {count} |"
        for concept, count in summary["top_candidate_frequency"].items()
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Audit semantic candidates for uncovered development queries"
    )
    parser.add_argument("--coverage", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-markdown", type=Path, required=True)
    parser.add_argument("--output-csv", type=Path, required=True)
    parser.add_argument("--acceptance-threshold", type=float, default=0.65)
    parser.add_argument("--review-margin", type=float, default=0.10)
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args()

    coverage = json.loads(args.coverage.read_text(encoding="utf-8"))
    uncovered = [row for row in coverage["questions"] if not row["query_concepts"]]
    ontology = OntologyService(semantic_encoder=SentenceTransformerEncoder())
    candidate_batches = ontology.semantic_candidates_batch(
        [row["query"] for row in uncovered], limit=args.limit
    )

    rows = []
    for source, candidates in zip(uncovered, candidate_batches, strict=True):
        candidate_rows = [
            {
                "concept": candidate.concept,
                "label": candidate.label,
                "score": candidate.score,
            }
            for candidate in candidates
        ]
        top_score = candidate_rows[0]["score"] if candidate_rows else 0.0
        rows.append(
            {
                "question_id": source["question_id"],
                "query": source["query"],
                "gold_concepts": source["gold_concepts"],
                "hybrid_rank": source["hybrid_rank"],
                "ontology_rank": source["ontology_rank"],
                "category": classify_candidate(
                    top_score,
                    acceptance_threshold=args.acceptance_threshold,
                    review_margin=args.review_margin,
                ),
                "candidates": candidate_rows,
            }
        )

    rows.sort(
        key=lambda row: (
            -(row["candidates"][0]["score"] if row["candidates"] else 0.0),
            row["question_id"],
        )
    )
    categories = Counter(row["category"] for row in rows)
    top_candidates = Counter(
        row["candidates"][0]["concept"] for row in rows if row["candidates"]
    )
    payload = {
        "coverage_source": str(args.coverage),
        "scope": "development queries without accepted concepts",
        "acceptance_threshold": args.acceptance_threshold,
        "review_margin": args.review_margin,
        "candidate_limit": args.limit,
        "summary": {
            "uncovered_queries": len(rows),
            "categories": dict(sorted(categories.items())),
            "top_candidate_frequency": dict(top_candidates.most_common(15)),
        },
        "queries": rows,
    }

    for output in (args.output_json, args.output_markdown, args.output_csv):
        output.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    args.output_markdown.write_text(render_markdown(payload), encoding="utf-8")
    with args.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "question_id",
                "category",
                "top_candidate",
                "top_score",
                "query",
                "gold_concepts",
                "review_decision",
                "review_note",
            ],
        )
        writer.writeheader()
        for row in rows:
            top = row["candidates"][0] if row["candidates"] else None
            writer.writerow(
                {
                    "question_id": row["question_id"],
                    "category": row["category"],
                    "top_candidate": top["concept"] if top else "",
                    "top_score": f"{top['score']:.6f}" if top else "",
                    "query": row["query"],
                    "gold_concepts": ";".join(row["gold_concepts"]),
                    "review_decision": "",
                    "review_note": "",
                }
            )
    print(json.dumps(payload["summary"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
