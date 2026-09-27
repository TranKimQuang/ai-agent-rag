"""Calibrate EvidenceGate on QASPER development without touching held-out data.

The first half of development papers selects thresholds; the second half is an
internal verification split. Positive cases are labelled supported only when a
QASPER gold chunk reaches the top three passages exposed to the answer model.
Deterministic wrong-paper pairings provide synthetic unsupported cases.
"""

import argparse
import itertools
import json
from dataclasses import asdict, dataclass
from pathlib import Path

from app.agent.service import EvidenceGate, EvidenceGateConfig
from app.models import Chunk, ConceptLinkingMethod, SearchMethod, SearchResult
from app.ontology.service import OntologyService
from app.rag.retriever import InMemoryHybridRetriever, SentenceTransformerEncoder

DEFAULT_DATASET = Path(
    "evaluation/qasper_train_v3/qasper_train_development.json"
)


@dataclass(frozen=True)
class GateExample:
    question_id: str
    question: str
    expected: bool
    kind: str
    results: list[SearchResult]


def metrics(gate: EvidenceGate, examples: list[GateExample]) -> dict[str, float | int]:
    tp = fp = tn = fn = 0
    for example in examples:
        predicted = gate.evaluate(example.question, example.results).accepted
        if predicted and example.expected:
            tp += 1
        elif predicted:
            fp += 1
        elif example.expected:
            fn += 1
        else:
            tn += 1
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    specificity = tn / (tn + fp) if tn + fp else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    total = tp + fp + tn + fn
    return {
        "examples": total,
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "accuracy": (tp + tn) / total if total else 0.0,
        "precision": precision,
        "recall": recall,
        "specificity": specificity,
        "balanced_accuracy": (recall + specificity) / 2,
        "f1": f1,
    }


def build_examples(
    questions: list[dict[str, object]],
    paper_ids: list[str],
    retriever: InMemoryHybridRetriever,
    *,
    limit: int,
) -> list[GateExample]:
    next_paper = {
        paper_id: paper_ids[(index + 1) % len(paper_ids)]
        for index, paper_id in enumerate(paper_ids)
    }
    examples: list[GateExample] = []
    for item in questions:
        paper_id = str(item["paper_id"])
        if paper_id not in next_paper:
            continue
        question = str(item["query"])
        gold = {str(value) for value in item["relevant_chunk_ids"]}
        supported_results = retriever.search(
            question,
            limit,
            SearchMethod.HYBRID_ONTOLOGY_RERANK,
            paper_id,
        )
        gold_in_model_context = any(
            result.chunk_id in gold for result in supported_results[:3]
        )
        examples.append(
            GateExample(
                question_id=str(item["id"]),
                question=question,
                expected=gold_in_model_context,
                kind="correct_paper",
                results=supported_results,
            )
        )
        examples.append(
            GateExample(
                question_id=str(item["id"]),
                question=question,
                expected=False,
                kind="wrong_paper",
                results=retriever.search(
                    question,
                    limit,
                    SearchMethod.HYBRID_ONTOLOGY_RERANK,
                    next_paper[paper_id],
                ),
            )
        )
    return examples


def candidate_configs() -> list[EvidenceGateConfig]:
    return [
        EvidenceGateConfig(*values)
        for values in itertools.product(
            [0.65, 0.80, 0.95],
            [0, 1, 2, 3],
            [0.55, 0.60, 0.65, 0.70],
            [2, 3],
            [0.30, 0.40, 0.50],
            [2, 3],
        )
    ]


def selection_key(row: dict[str, object]) -> tuple[float, float, float, float]:
    scores = row["metrics"]
    return (
        float(scores["balanced_accuracy"]),
        float(scores["f1"]),
        float(scores["precision"]),
        float(scores["recall"]),
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Tune the evidence gate on a paper-separated QASPER development split"
    )
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/evidence_gate_calibration.json"),
    )
    args = parser.parse_args()
    if not 3 <= args.limit <= 10:
        parser.error("--limit must be between 3 and 10")

    payload = json.loads(args.dataset.read_text(encoding="utf-8"))
    split_name = str(payload.get("metadata", {}).get("split", ""))
    if "heldout" in split_name.lower():
        raise ValueError("Evidence gate calibration must not use held-out data")
    paper_ids = [str(value) for value in payload["metadata"]["paper_ids"]]
    midpoint = len(paper_ids) // 2
    selection_papers = paper_ids[:midpoint]
    verification_papers = paper_ids[midpoint:]

    encoder = SentenceTransformerEncoder()
    ontology = OntologyService(
        semantic_encoder=encoder,
        linking_method=ConceptLinkingMethod.HYBRID,
        linking_threshold=0.65,
    )
    chunks = [Chunk.model_validate(item) for item in payload["chunks"]]
    chunks, concept_links = ontology.index_chunks(chunks)
    retriever = InMemoryHybridRetriever(
        semantic_encoder=encoder,
        ontology_service=ontology,
    )
    retriever.add(chunks)

    questions = payload["questions"]
    selection_examples = build_examples(
        questions, selection_papers, retriever, limit=args.limit
    )
    verification_examples = build_examples(
        questions, verification_papers, retriever, limit=args.limit
    )
    baseline_config = EvidenceGateConfig()
    baseline = {
        "config": asdict(baseline_config),
        "selection": metrics(EvidenceGate(baseline_config), selection_examples),
        "verification": metrics(EvidenceGate(baseline_config), verification_examples),
    }

    candidates = []
    for config in candidate_configs():
        candidates.append(
            {
                "config": asdict(config),
                "metrics": metrics(EvidenceGate(config), selection_examples),
            }
        )
    selected = max(candidates, key=selection_key)
    selected_config = EvidenceGateConfig(**selected["config"])
    report = {
        "dataset": str(args.dataset),
        "source_split": split_name,
        "heldout_used": False,
        "selection_papers": selection_papers,
        "verification_papers": verification_papers,
        "concept_links": concept_links,
        "labelling": {
            "positive": "correct-paper query with QASPER gold evidence in top 3",
            "negative": "gold missing from top 3 or deterministic wrong-paper query",
            "warning": "These are proxy labels; QASPER gold evidence may be incomplete.",
        },
        "selection_objective": (
            "balanced accuracy, then F1, precision and recall on selection papers"
        ),
        "baseline": baseline,
        "selected": {
            "config": asdict(selected_config),
            "selection": selected["metrics"],
            "verification": metrics(
                EvidenceGate(selected_config), verification_examples
            ),
        },
        "candidate_count": len(candidates),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2), flush=True)
    print(f"Saved: {args.output}", flush=True)


if __name__ == "__main__":
    main()
