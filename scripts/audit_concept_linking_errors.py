from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any

from app.models import ConceptLink
from app.ontology.service import OntologyService
from app.rag.retriever import SentenceTransformerEncoder
from scripts.run_benchmark import load_dataset


def classify_coverage_row(row: dict[str, Any]) -> str:
    """Assign a descriptive error group without pretending to create gold labels."""
    query_concepts = row.get("query_concepts", [])
    gold_concepts = row.get("gold_concepts", [])
    if row.get("gold_has_ontology_relation"):
        return "useful_relation"
    if not query_concepts and not gold_concepts:
        return "missing_query_and_gold_concepts"
    if not query_concepts:
        return "missing_query_concept"
    if not gold_concepts:
        return "missing_gold_concept"
    return "missing_relation_or_query_mismatch"


def _candidate_rows(
    phrases: list[str], candidate_batches: list[list[ConceptLink]], limit: int
) -> list[dict[str, object]]:
    best: dict[str, dict[str, object]] = {}
    for phrase, candidates in zip(phrases, candidate_batches, strict=True):
        for candidate in candidates:
            current = best.get(candidate.concept)
            if current is None or candidate.score > float(current["score"]):
                best[candidate.concept] = {
                    "concept": candidate.concept,
                    "label": candidate.label,
                    "score": candidate.score,
                    "phrase": phrase,
                }
    return sorted(
        best.values(), key=lambda item: (-float(item["score"]), str(item["concept"]))
    )[:limit]


def query_candidate_proposals(
    ontology: OntologyService, queries: list[str], *, limit: int
) -> list[list[dict[str, object]]]:
    """Generate phrase-aware suggestions in one embedding batch."""
    phrases_by_query = [ontology.query_phrases(query) for query in queries]
    flat_phrases = [phrase for phrases in phrases_by_query for phrase in phrases]
    flat_candidates = ontology.semantic_candidates_batch(flat_phrases, limit=limit)
    proposals: list[list[dict[str, object]]] = []
    offset = 0
    for phrases in phrases_by_query:
        end = offset + len(phrases)
        proposals.append(
            _candidate_rows(phrases, flat_candidates[offset:end], limit)
        )
        offset = end
    return proposals


def evidence_candidate_proposals(
    ontology: OntologyService,
    evidence_groups: list[list[tuple[str, str]]],
    *,
    limit: int,
) -> list[list[dict[str, object]]]:
    """Aggregate semantic proposals over every gold chunk of each question."""
    flat_sources = [source for group in evidence_groups for source, _ in group]
    flat_texts = [text for group in evidence_groups for _, text in group]
    flat_candidates = ontology.semantic_candidates_batch(flat_texts, limit=limit)
    proposals: list[list[dict[str, object]]] = []
    offset = 0
    for group in evidence_groups:
        end = offset + len(group)
        proposals.append(
            _candidate_rows(
                flat_sources[offset:end], flat_candidates[offset:end], limit
            )
        )
        offset = end
    return proposals


def render_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Concept-linking error audit",
        "",
        f"- Dataset: `{payload['dataset']}`",
        f"- Questions: **{summary['questions']}**",
        f"- Usage policy: **{payload['usage_policy']}**",
        "",
        "The groups below are descriptive triage labels, not automatic gold labels.",
        "",
        "## Summary",
        "",
        "| Group | Questions |",
        "|---|---:|",
    ]
    lines.extend(
        f"| {group} | {count} |" for group, count in summary["groups"].items()
    )
    lines.extend(
        [
            "",
            "## Review queue",
            "",
            "| Group | Query concepts | Gold concepts | Query proposal | Evidence proposal | Question |",
            "|---|---|---|---|---|---|",
        ]
    )
    for row in payload["questions"]:
        proposal = row["query_candidate_proposals"][0]
        evidence_proposal = row["gold_candidate_proposals"][0]
        lines.append(
            "| {group} | {query_concepts} | {gold_concepts} | {candidate} "
            "({score:.4f}) | {evidence_candidate} ({evidence_score:.4f}) | {query} |".format(
                group=row["error_group"],
                query_concepts=", ".join(row["query_concepts"]) or "—",
                gold_concepts=", ".join(row["gold_concepts"]) or "—",
                candidate=proposal["concept"] if proposal else "—",
                score=float(proposal["score"]) if proposal else 0.0,
                evidence_candidate=(
                    evidence_proposal["concept"] if evidence_proposal else "—"
                ),
                evidence_score=(
                    float(evidence_proposal["score"]) if evidence_proposal else 0.0
                ),
                query=row["query"].replace("|", "\\|"),
            )
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create a review queue for query/evidence Ontology coverage errors"
    )
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--coverage", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-csv", type=Path, required=True)
    parser.add_argument("--output-markdown", type=Path, required=True)
    parser.add_argument("--candidate-limit", type=int, default=5)
    parser.add_argument(
        "--usage-policy",
        choices=("development_labeling", "locked_validation_analysis_only"),
        required=True,
    )
    args = parser.parse_args()
    if args.candidate_limit < 1:
        raise ValueError("candidate-limit must be at least 1")

    chunks, questions = load_dataset(args.dataset)
    chunks_by_id = {chunk.id: chunk for chunk in chunks}
    questions_by_id = {question.question_id: question for question in questions}
    coverage = json.loads(args.coverage.read_text(encoding="utf-8"))
    coverage_rows = coverage["questions"]

    ontology = OntologyService(semantic_encoder=SentenceTransformerEncoder())
    query_proposals = query_candidate_proposals(
        ontology,
        [row["query"] for row in coverage_rows],
        limit=args.candidate_limit,
    )
    evidence_groups: list[list[tuple[str, str]]] = []
    for source in coverage_rows:
        question = questions_by_id[source["question_id"]]
        evidence_groups.append(
            [
                (chunk_id, chunks_by_id[chunk_id].text)
                for chunk_id in question.relevant_chunk_ids
                if chunk_id in chunks_by_id
            ]
        )
    gold_proposals = evidence_candidate_proposals(
        ontology, evidence_groups, limit=args.candidate_limit
    )

    rows: list[dict[str, object]] = []
    for source, proposals, evidence_proposals in zip(
        coverage_rows, query_proposals, gold_proposals, strict=True
    ):
        question = questions_by_id[source["question_id"]]
        gold_chunks = [
            chunks_by_id[chunk_id]
            for chunk_id in question.relevant_chunk_ids
            if chunk_id in chunks_by_id
        ]
        evidence = " ".join(chunk.text for chunk in gold_chunks)
        relation_supported = [
            proposal
            for proposal in proposals
            if ontology.score_concept_names(
                [str(proposal["concept"])], source["gold_concepts"]
            ).score
            > 0
        ]
        if source["gold_has_ontology_relation"]:
            review_hint = "keep_current_relation_then_verify_labels"
        elif relation_supported:
            review_hint = "review_candidate_related_to_gold"
        elif not source["gold_concepts"]:
            review_hint = "review_gold_evidence_concepts_first"
        else:
            review_hint = "no_supported_candidate_review_vocabulary_or_labels"
        rows.append(
            {
                "question_id": source["question_id"],
                "document_id": question.document_id,
                "error_group": classify_coverage_row(source),
                "query": source["query"],
                "query_concepts": source["query_concepts"],
                "gold_concepts": source["gold_concepts"],
                "gold_has_ontology_relation": source[
                    "gold_has_ontology_relation"
                ],
                "hybrid_rank": source["hybrid_rank"],
                "ontology_rank": source["ontology_rank"],
                "query_candidate_proposals": proposals,
                "gold_candidate_proposals": evidence_proposals,
                "relation_supported_query_proposals": relation_supported,
                "review_hint": review_hint,
                "gold_evidence_excerpt": evidence[:500],
            }
        )

    priority = {
        "missing_relation_or_query_mismatch": 0,
        "missing_query_concept": 1,
        "missing_gold_concept": 2,
        "missing_query_and_gold_concepts": 3,
        "useful_relation": 4,
    }
    rows.sort(key=lambda row: (priority[str(row["error_group"])], str(row["question_id"])))
    groups = Counter(str(row["error_group"]) for row in rows)
    payload = {
        "dataset": str(args.dataset),
        "coverage_source": str(args.coverage),
        "usage_policy": args.usage_policy,
        "candidate_limit": args.candidate_limit,
        "summary": {
            "questions": len(rows),
            "groups": {
                group: groups.get(group, 0)
                for group in priority
            },
        },
        "questions": rows,
    }

    for output in (args.output_json, args.output_csv, args.output_markdown):
        output.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    args.output_markdown.write_text(render_markdown(payload), encoding="utf-8")
    with args.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
        fieldnames = [
            "question_id",
            "document_id",
            "error_group",
            "query",
            "query_concepts",
            "gold_concepts",
            "top_query_candidate",
            "top_query_score",
            "top_query_phrase",
            "top_gold_candidate",
            "top_gold_score",
            "top_gold_chunk_id",
            "relation_supported_candidate",
            "review_hint",
            "gold_evidence_excerpt",
            "hybrid_rank",
            "ontology_rank",
            "review_query_concepts",
            "review_gold_concepts",
            "review_relation",
            "review_note",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            proposals = row["query_candidate_proposals"]
            top = proposals[0] if proposals else None
            gold_proposals = row["gold_candidate_proposals"]
            top_gold = gold_proposals[0] if gold_proposals else None
            relation_supported = row["relation_supported_query_proposals"]
            supported = relation_supported[0] if relation_supported else None
            writer.writerow(
                {
                    "question_id": row["question_id"],
                    "document_id": row["document_id"],
                    "error_group": row["error_group"],
                    "query": row["query"],
                    "query_concepts": ";".join(row["query_concepts"]),
                    "gold_concepts": ";".join(row["gold_concepts"]),
                    "top_query_candidate": top["concept"] if top else "",
                    "top_query_score": f"{float(top['score']):.6f}" if top else "",
                    "top_query_phrase": top["phrase"] if top else "",
                    "top_gold_candidate": top_gold["concept"] if top_gold else "",
                    "top_gold_score": (
                        f"{float(top_gold['score']):.6f}" if top_gold else ""
                    ),
                    "top_gold_chunk_id": top_gold["phrase"] if top_gold else "",
                    "relation_supported_candidate": (
                        supported["concept"] if supported else ""
                    ),
                    "review_hint": row["review_hint"],
                    "gold_evidence_excerpt": row["gold_evidence_excerpt"],
                    "hybrid_rank": row["hybrid_rank"],
                    "ontology_rank": row["ontology_rank"],
                    "review_query_concepts": "",
                    "review_gold_concepts": "",
                    "review_relation": "",
                    "review_note": "",
                }
            )
    print(json.dumps(payload["summary"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
