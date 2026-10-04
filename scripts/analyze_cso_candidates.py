import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import quote

import numpy as np

from app.ontology.service import OntologyService, normalize_text
from app.rag.retriever import SentenceTransformerEncoder

DEFAULT_SEEDS = [
    "artificial intelligence",
    "information retrieval",
    "machine learning",
    "natural language processing",
    "question answering",
    "semantic search",
]
_QUESTION_WORDS = {
    "a",
    "an",
    "are",
    "did",
    "do",
    "does",
    "for",
    "how",
    "in",
    "is",
    "of",
    "on",
    "the",
    "they",
    "to",
    "used",
    "using",
    "was",
    "were",
    "what",
    "which",
}


@dataclass(frozen=True)
class CSOVocabulary:
    documents: dict[str, str]
    depths: dict[str, int]
    rows: int
    labelled_topics: int


def cso_uri(label: str) -> str:
    slug = quote(label.replace(" ", "_"), safe="_-")
    return f"https://cso.kmi.open.ac.uk/topics/{slug}"


def lexical_tokens(text: str) -> set[str]:
    tokens = set()
    for token in normalize_text(text).split():
        if token in _QUESTION_WORDS:
            continue
        if token.endswith("ies") and len(token) > 4:
            token = f"{token[:-3]}y"
        elif token.endswith("s") and len(token) > 3 and not token.endswith("ss"):
            token = token[:-1]
        tokens.add(token)
    return tokens


def has_lexical_support(query: str, candidate: str) -> bool:
    candidate_tokens = lexical_tokens(candidate)
    return bool(candidate_tokens) and candidate_tokens <= lexical_tokens(query)


def load_cso_branch(path: Path, seeds: list[str]) -> CSOVocabulary:
    rows: list[tuple[str, str, str]] = []
    primary_by_alias: dict[str, str] = {}
    labelled_topics: set[str] = set()
    with path.open(encoding="utf-8", newline="") as handle:
        for triple in csv.reader(handle, delimiter=";"):
            if len(triple) != 3:
                continue
            subject, predicate, object_value = (value.strip() for value in triple)
            rows.append((subject, predicate, object_value))
            if predicate == "rdfs:label":
                labelled_topics.add(subject)
            elif predicate == "klink:primaryLabel":
                primary_by_alias[subject] = object_value

    def primary(label: str) -> str:
        seen: set[str] = set()
        while label in primary_by_alias and label not in seen:
            seen.add(label)
            next_label = primary_by_alias[label]
            if next_label == label:
                break
            label = next_label
        return label

    aliases: dict[str, set[str]] = defaultdict(set)
    children: dict[str, set[str]] = defaultdict(set)
    for topic in labelled_topics:
        aliases[primary(topic)].add(topic)
    for subject, predicate, object_value in rows:
        if predicate == "klink:primaryLabel":
            aliases[primary(object_value)].add(subject)
        elif predicate == "klink:relatedEquivalent":
            aliases[primary(subject)].add(object_value)
        elif predicate == "klink:broaderGeneric":
            broader = primary(subject)
            narrower = primary(object_value)
            if broader != narrower:
                children[broader].add(narrower)

    normalized_lookup = {
        normalize_text(label): label for label in aliases if normalize_text(label)
    }
    canonical_seeds = [
        normalized_lookup[normalize_text(seed)]
        for seed in seeds
        if normalize_text(seed) in normalized_lookup
    ]
    depths: dict[str, int] = {}
    queue = deque((seed, 0) for seed in canonical_seeds)
    while queue:
        topic, depth = queue.popleft()
        if topic in depths and depths[topic] <= depth:
            continue
        depths[topic] = depth
        queue.extend((child, depth + 1) for child in children.get(topic, ()))

    documents = {
        topic: " ".join([topic, *sorted(aliases.get(topic, set()) - {topic})])
        for topic in sorted(depths)
    }
    return CSOVocabulary(
        documents=documents,
        depths=depths,
        rows=len(rows),
        labelled_topics=len(labelled_topics),
    )


def render_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# CSO candidate audit for uncovered development queries",
        "",
        (
            "This is a candidate-generation audit only. It does not automatically add "
            "topics to the local ontology and does not use validation or final-test "
            "retrieval results."
        ),
        "",
        "## Summary",
        "",
        f"- CSO SHA-256: `{payload['cso_sha256']}`",
        f"- Parsed triples: **{summary['cso_rows']}**",
        f"- Labelled CSO topics: **{summary['cso_labelled_topics']}**",
        f"- Topics inside selected branches: **{summary['selected_topics']}**",
        f"- Uncovered development queries: **{summary['queries']}**",
        f"- Top score >= 0.60: **{summary['top_score_at_least_0_60']}**",
        f"- Top score >= 0.50: **{summary['top_score_at_least_0_50']}**",
        f"- Conservative shortlist: **{summary['conservative_shortlist']}**",
        "",
        "## Review queue",
        "",
        "| Priority | Top score | Candidate | Lexical support | Query | Gold concepts |",
        "|---|---:|---|---|---|---|",
    ]
    for row in payload["queries"]:
        top = row["candidates"][0]
        query = row["query"].replace("|", "\\|")
        gold = ", ".join(row["gold_concepts"]) or "—"
        lines.append(
            f"| {row['review_priority']} | {top['score']:.4f} | {top['label']} | "
            f"{'yes' if top['lexical_support'] else 'no'} | {query} | {gold} |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate CSO topic candidates for uncovered development queries"
    )
    parser.add_argument("--cso", type=Path, required=True)
    parser.add_argument("--coverage", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-markdown", type=Path, required=True)
    parser.add_argument("--output-csv", type=Path, required=True)
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--seed", action="append", dest="seeds")
    args = parser.parse_args()

    seeds = args.seeds or DEFAULT_SEEDS
    vocabulary = load_cso_branch(args.cso, seeds)
    if not vocabulary.documents:
        raise RuntimeError("No CSO topics were found below the selected seeds")
    coverage = json.loads(args.coverage.read_text(encoding="utf-8"))
    uncovered = [row for row in coverage["questions"] if not row["query_concepts"]]

    ontology = OntologyService()
    local_labels = {normalize_text(label) for label in ontology.vocabulary_labels()}
    labels = list(vocabulary.documents)
    encoder = SentenceTransformerEncoder()
    topic_vectors = encoder.encode([vocabulary.documents[label] for label in labels])
    query_vectors = encoder.encode([row["query"] for row in uncovered])
    score_matrix = query_vectors @ topic_vectors.T

    rows = []
    for source, scores in zip(uncovered, score_matrix, strict=True):
        candidate_indexes = np.argsort(scores)[::-1][: args.limit]
        candidates = [
            {
                "label": labels[int(index)],
                "uri": cso_uri(labels[int(index)]),
                "score": max(min(float(scores[int(index)]), 1.0), 0.0),
                "branch_depth": vocabulary.depths[labels[int(index)]],
                "already_local": normalize_text(labels[int(index)]) in local_labels,
                "lexical_support": has_lexical_support(
                    source["query"], labels[int(index)]
                ),
            }
            for index in candidate_indexes
        ]
        top = candidates[0]
        priority = (
            "high"
            if top["score"] >= 0.60 and top["lexical_support"]
            else "medium"
            if top["score"] >= 0.60
            else "low"
        )
        rows.append(
            {
                "question_id": source["question_id"],
                "query": source["query"],
                "gold_concepts": source["gold_concepts"],
                "review_priority": priority,
                "candidates": candidates,
            }
        )
    rows.sort(key=lambda row: -row["candidates"][0]["score"])
    top_frequency = Counter(row["candidates"][0]["label"] for row in rows)
    payload = {
        "scope": "development queries uncovered after local query-type linking",
        "cso_source": args.cso.as_posix(),
        "cso_sha256": hashlib.sha256(args.cso.read_bytes()).hexdigest(),
        "coverage_source": args.coverage.as_posix(),
        "seeds": seeds,
        "summary": {
            "cso_rows": vocabulary.rows,
            "cso_labelled_topics": vocabulary.labelled_topics,
            "selected_topics": len(vocabulary.documents),
            "queries": len(rows),
            "top_score_at_least_0_60": sum(
                row["candidates"][0]["score"] >= 0.60 for row in rows
            ),
            "top_score_at_least_0_50": sum(
                row["candidates"][0]["score"] >= 0.50 for row in rows
            ),
            "conservative_shortlist": sum(
                row["review_priority"] == "high" for row in rows
            ),
            "top_candidate_frequency": dict(top_frequency.most_common(15)),
        },
        "queries": rows,
    }

    for output in (args.output_json, args.output_markdown, args.output_csv):
        output.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    args.output_markdown.write_text(render_markdown(payload), encoding="utf-8")
    with args.output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "question_id",
                "top_candidate",
                "top_score",
                "already_local",
                "lexical_support",
                "review_priority",
                "query",
                "gold_concepts",
                "review_decision",
                "review_note",
            ],
        )
        writer.writeheader()
        for row in rows:
            top = row["candidates"][0]
            writer.writerow(
                {
                    "question_id": row["question_id"],
                    "top_candidate": top["label"],
                    "top_score": f"{top['score']:.6f}",
                    "already_local": top["already_local"],
                    "lexical_support": top["lexical_support"],
                    "review_priority": row["review_priority"],
                    "query": row["query"],
                    "gold_concepts": ";".join(row["gold_concepts"]),
                    "review_decision": "",
                    "review_note": "",
                }
            )
    print(json.dumps(payload["summary"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
