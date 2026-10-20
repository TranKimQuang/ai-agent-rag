from __future__ import annotations

import argparse
import hashlib
import json
import random
from collections import Counter, defaultdict
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path

from app.evaluation.qasper import QasperPaperBenchmark, build_split, convert_qasper_paper
from app.evaluation.qasper_protocol import collect_excluded_paper_ids
from app.models import ConceptLinkingMethod
from app.ontology.service import OntologyService
from scripts.prepare_qasper_concept_validation import (
    build_blinded_review_rows,
    build_concept_catalog_rows,
    write_csv,
)
from scripts.prepare_qasper_parquet_subset import parquet_row_to_original
from scripts.prepare_qasper_result_validation import EXPECTED_SOURCE_SHA256, file_sha256


def collect_excluded_question_ids(paths: list[Path]) -> set[str]:
    question_ids: set[str] = set()
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        question_ids.update(str(question["id"]) for question in payload["questions"])
    return question_ids


def taxonomy_concepts(service: OntologyService) -> set[str]:
    """Return active concepts that participate in a direct SKOS hierarchy edge."""
    concepts = service.vocabulary_concept_names()
    children = {
        concept for concept in concepts if service.broader_concept_names(concept)
    }
    parents = {
        parent
        for concept in children
        for parent in service.broader_concept_names(concept)
    }
    return children | parents


def select_taxonomy_questions(
    papers: list[QasperPaperBenchmark],
    service: OntologyService,
    *,
    per_concept: int,
    max_questions: int,
    max_questions_per_paper: int,
    seed: int,
    semantic_threshold: float | None = None,
) -> tuple[list[QasperPaperBenchmark], dict[str, list[str]]]:
    """Select explicit taxonomy candidates with deterministic concept balancing."""
    if min(per_concept, max_questions, max_questions_per_paper) < 1:
        raise ValueError("Selection limits must be at least 1")
    targets = taxonomy_concepts(service)
    candidates: dict[str, list[tuple[QasperPaperBenchmark, dict[str, object]]]] = (
        defaultdict(list)
    )
    question_concepts: dict[str, list[str]] = {}
    question_rows = [
        (paper, question) for paper in papers for question in paper.questions
    ]
    semantic_by_question: dict[str, set[str]] = {}
    if semantic_threshold is not None:
        semantic_links = service.link_concepts_batch(
            [str(question["query"]) for _, question in question_rows],
            ConceptLinkingMethod.SEMANTIC,
            threshold=semantic_threshold,
            limit=3,
        )
        semantic_by_question = {
            str(question["id"]): {link.concept for link in links} & targets
            for (_, question), links in zip(question_rows, semantic_links, strict=True)
        }

    for paper, question in question_rows:
        question_id = str(question["id"])
        linked = sorted(
            {
                concept.rsplit("#", maxsplit=1)[-1]
                for concept in service.identify_concepts(str(question["query"]))
            }
            & targets
            | semantic_by_question.get(question_id, set())
        )
        if not linked:
            continue
        question_concepts[question_id] = linked
        for concept in linked:
            candidates[concept].append((paper, question))

    rng = random.Random(seed)
    for values in candidates.values():
        rng.shuffle(values)

    selected_ids: set[str] = set()
    selected_by_paper: dict[str, list[dict[str, object]]] = defaultdict(list)
    selected_per_concept: Counter[str] = Counter()
    ordered_concepts = sorted(candidates, key=lambda name: (len(candidates[name]), name))
    made_progress = True
    while len(selected_ids) < max_questions and made_progress:
        made_progress = False
        for concept in ordered_concepts:
            if selected_per_concept[concept] >= per_concept:
                continue
            for paper, question in candidates[concept]:
                question_id = str(question["id"])
                if question_id in selected_ids:
                    continue
                if len(selected_by_paper[paper.paper_id]) >= max_questions_per_paper:
                    continue
                selected_ids.add(question_id)
                selected_by_paper[paper.paper_id].append(question)
                for linked_concept in question_concepts[question_id]:
                    selected_per_concept[linked_concept] += 1
                made_progress = True
                break
            if len(selected_ids) >= max_questions:
                break

    selected_papers = [
        replace(paper, questions=selected_by_paper[paper.paper_id])
        for paper in papers
        if selected_by_paper[paper.paper_id]
    ]
    selected_strata = {
        question_id: question_concepts[question_id]
        for question_id in sorted(selected_ids)
    }
    return selected_papers, selected_strata


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare a taxonomy-focused QASPER concept-linking development set"
    )
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--exclude-paper-dataset", type=Path, action="append", default=[]
    )
    parser.add_argument(
        "--exclude-question-dataset", type=Path, action="append", default=[]
    )
    parser.add_argument("--per-concept", type=int, default=5)
    parser.add_argument("--max-questions", type=int, default=80)
    parser.add_argument("--max-questions-per-paper", type=int, default=3)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument(
        "--semantic-threshold",
        type=float,
        help="Optionally use semantic candidates only for constructing the review queue.",
    )
    parser.add_argument(
        "--created-on", default=datetime.now(tz=UTC).date().isoformat()
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source_hash = file_sha256(args.input)
    if source_hash != EXPECTED_SOURCE_SHA256:
        raise ValueError(
            f"Unexpected QASPER source SHA-256: {source_hash}; "
            f"expected {EXPECTED_SOURCE_SHA256}"
        )
    try:
        import pyarrow.parquet as pq
    except ImportError as exc:
        raise RuntimeError("Install pyarrow to prepare the taxonomy pool") from exc

    rows = pq.read_table(args.input).to_pylist()
    payload = dict(parquet_row_to_original(row) for row in rows)
    excluded_papers = collect_excluded_paper_ids(args.exclude_paper_dataset)
    excluded_questions = collect_excluded_question_ids(args.exclude_question_dataset)
    papers = []
    for paper_id in sorted(payload):
        if paper_id in excluded_papers:
            continue
        paper = convert_qasper_paper(paper_id, payload[paper_id], max_questions=1000)
        unused_questions = [
            question
            for question in paper.questions
            if str(question["id"]) not in excluded_questions
        ]
        papers.append(replace(paper, questions=unused_questions))
    papers = [paper for paper in papers if paper.questions]
    semantic_encoder = None
    if args.semantic_threshold is not None:
        from app.rag.retriever import SentenceTransformerEncoder

        semantic_encoder = SentenceTransformerEncoder()
    service = OntologyService(semantic_encoder=semantic_encoder)
    selected_papers, strata = select_taxonomy_questions(
        papers,
        service,
        per_concept=args.per_concept,
        max_questions=args.max_questions,
        max_questions_per_paper=args.max_questions_per_paper,
        seed=args.seed,
        semantic_threshold=args.semantic_threshold,
    )
    if not selected_papers:
        raise ValueError("No taxonomy-focused questions were found")

    dataset = build_split(selected_papers, split="taxonomy_concept_development_v22")
    selected_ids = set(dataset["metadata"]["paper_ids"])
    overlap = sorted(selected_ids & excluded_papers)
    if overlap:
        raise ValueError(f"Taxonomy development overlaps excluded papers: {overlap}")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    dataset_path = args.output_dir / "qasper_taxonomy_development.json"
    dataset_content = (json.dumps(dataset, ensure_ascii=False, indent=2) + "\n").encode()
    dataset_path.write_bytes(dataset_content)
    packet_path = args.output_dir / "blinded_labeling_packet.csv"
    packet_content = write_csv(packet_path, build_blinded_review_rows(dataset))
    catalog_path = args.output_dir / "active_concept_catalog.csv"
    catalog_content = write_csv(catalog_path, build_concept_catalog_rows())
    strata_path = args.output_dir / "selection_strata.json"
    strata_content = (json.dumps(strata, ensure_ascii=False, indent=2) + "\n").encode()
    strata_path.write_bytes(strata_content)

    counts = Counter(concept for concepts in strata.values() for concept in concepts)
    manifest = {
        "protocol": "QASPER taxonomy-focused concept development v22",
        "created_on": args.created_on,
        "source": "allenai/qasper qasper/train/0000.parquet",
        "source_sha256": source_hash,
        "selection_seed": args.seed,
        "selection_policy": {
            "candidate_rule": (
                "explicit alias or semantic candidate for a concept participating in "
                "a direct skos:broader edge"
                if args.semantic_threshold is not None
                else "explicit alias match to a concept in a direct skos:broader edge"
            ),
            "per_concept_limit": args.per_concept,
            "max_questions": args.max_questions,
            "max_questions_per_paper": args.max_questions_per_paper,
            "semantic_candidate_threshold": args.semantic_threshold,
            "limitation": (
                "Purpose-built diagnostic development data; semantic candidates are "
                "review prompts, not labels, and selection is not an unbiased estimate "
                "of general concept-linking performance."
            ),
        },
        "excluded_paper_dataset_files": [
            path.as_posix() for path in args.exclude_paper_dataset
        ],
        "excluded_question_dataset_files": [
            path.as_posix() for path in args.exclude_question_dataset
        ],
        "excluded_unique_protected_papers": len(excluded_papers),
        "excluded_previously_used_questions": len(excluded_questions),
        "paper_disjoint_from_validation_and_final": True,
        "question_disjoint_from_prior_development": True,
        "overlap_with_protected_papers": overlap,
        "development": {
            "file": dataset_path.name,
            "papers": len(dataset["metadata"]["paper_ids"]),
            "chunks": len(dataset["chunks"]),
            "questions": len(dataset["questions"]),
            "candidate_concept_counts": dict(sorted(counts.items())),
            "sha256": hashlib.sha256(dataset_content).hexdigest(),
            "labeling_packet": packet_path.name,
            "labeling_packet_sha256": hashlib.sha256(packet_content).hexdigest(),
            "concept_catalog": catalog_path.name,
            "concept_catalog_sha256": hashlib.sha256(catalog_content).hexdigest(),
            "selection_strata": strata_path.name,
            "selection_strata_sha256": hashlib.sha256(strata_content).hexdigest(),
            "label_status": "awaiting_independent_labels",
            "prediction_status": "not_run",
        },
        "policy": (
            "Use only for taxonomy mechanism development. Keep labeling packet blind, "
            "do not tune on validation v19/v21, and keep final test sealed."
        ),
    }
    (args.output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
