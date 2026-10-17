import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold

from app.models import ConceptLinkingMethod
from app.ontology.service import OntologyService
from app.rag.retriever import SentenceTransformerEncoder
from scripts.evaluate_cross_encoder_concept_linking import metrics
from scripts.run_concept_linking_benchmark import load_examples, validate_gold_concepts


def load_question_groups(path: Path) -> dict[str, str]:
    """Map QASPER question IDs to papers for leakage-safe grouped evaluation."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    mapping: dict[str, str] = {}
    for row in payload["questions"]:
        question_id = str(row["id"])
        if question_id in mapping:
            raise ValueError(f"Duplicate QASPER question ID: {question_id}")
        mapping[question_id] = str(row["paper_id"])
    return mapping


def supervised_oof_scores(
    examples: list[dict[str, Any]],
    embeddings: NDArray[np.float32],
    groups: list[str],
    labels: list[str],
    *,
    n_splits: int = 5,
    minimum_train_positives: int = 2,
) -> tuple[NDArray[np.float32], list[int], dict[str, int]]:
    """Return paper-disjoint out-of-fold probabilities for each observed label."""
    if len(examples) != len(embeddings) or len(examples) != len(groups):
        raise ValueError("Examples, embeddings, and groups must have equal lengths")
    unique_groups = len(set(groups))
    if unique_groups < 2:
        raise ValueError("At least two paper groups are required")
    folds = min(n_splits, unique_groups)
    scores = np.zeros((len(examples), len(labels)), dtype=np.float32)
    fold_ids = [-1] * len(examples)
    trained_counts = Counter[str]()
    splitter = GroupKFold(n_splits=folds)
    targets = np.asarray(
        [[int(label in example["gold_concepts"]) for label in labels] for example in examples],
        dtype=np.int8,
    )

    for fold_id, (train_indices, test_indices) in enumerate(
        splitter.split(embeddings, groups=groups)
    ):
        for index in test_indices:
            fold_ids[int(index)] = fold_id
        for label_index, label in enumerate(labels):
            train_targets = targets[train_indices, label_index]
            positives = int(train_targets.sum())
            if (
                positives < minimum_train_positives
                or positives == len(train_targets)
            ):
                continue
            classifier = LogisticRegression(
                class_weight="balanced",
                max_iter=1000,
                random_state=0,
            )
            classifier.fit(embeddings[train_indices], train_targets)
            scores[test_indices, label_index] = classifier.predict_proba(
                embeddings[test_indices]
            )[:, 1]
            trained_counts[label] += 1

    return scores, fold_ids, dict(trained_counts)


def predictions_at_threshold(
    alias_predictions: list[set[str]],
    scores: NDArray[np.float32],
    labels: list[str],
    threshold: float,
) -> list[set[str]]:
    predictions: list[set[str]] = []
    for alias, row in zip(alias_predictions, scores, strict=True):
        selected = set(alias)
        selected.update(
            label for label, score in zip(labels, row, strict=True) if score >= threshold
        )
        predictions.append(selected)
    return predictions


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate a paper-disjoint supervised concept linker"
    )
    parser.add_argument("--dataset", type=Path, nargs="+", required=True)
    parser.add_argument("--label-audit", type=Path, nargs="*", default=[])
    parser.add_argument("--qasper-data", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument(
        "--thresholds",
        type=float,
        nargs="+",
        default=[0.50, 0.60, 0.70, 0.80, 0.90],
    )
    args = parser.parse_args()

    examples = load_examples(args.dataset, label_audits=args.label_audit)
    question_groups = load_question_groups(args.qasper_data)
    groups: list[str] = []
    for example in examples:
        question_id = str(example.get("source_question_id", ""))
        if question_id not in question_groups:
            raise ValueError(f"Question is absent from QASPER data: {question_id}")
        groups.append(question_groups[question_id])

    encoder = SentenceTransformerEncoder()
    service = OntologyService(semantic_encoder=encoder)
    validate_gold_concepts(service, examples)
    embeddings = encoder.encode([example["text"] for example in examples])
    labels = sorted({label for example in examples for label in example["gold_concepts"]})
    scores, fold_ids, trained_counts = supervised_oof_scores(
        examples,
        embeddings,
        groups,
        labels,
        n_splits=args.folds,
    )
    alias_predictions = [
        {
            link.concept
            for link in service.link_concepts(
                example["text"], ConceptLinkingMethod.ALIAS, limit=20
            )
        }
        for example in examples
    ]
    configurations = []
    predictions_by_threshold: dict[float, list[set[str]]] = {}
    for threshold in sorted(set(args.thresholds)):
        predictions = predictions_at_threshold(
            alias_predictions, scores, labels, threshold
        )
        configurations.append({"threshold": threshold, **metrics(examples, predictions)})
        predictions_by_threshold[threshold] = predictions
    configurations.sort(
        key=lambda row: (
            -row["f1"],
            -row["precision"],
            -row["exact_match"],
            -row["threshold"],
        )
    )
    best = configurations[0]
    best_predictions = predictions_by_threshold[best["threshold"]]
    label_counts = Counter(
        label for example in examples for label in example["gold_concepts"]
    )
    rows = [
        {
            "source_question_id": example.get("source_question_id"),
            "paper_id": group,
            "fold": fold_id,
            "text": example["text"],
            "gold_concepts": example["gold_concepts"],
            "alias_concepts": sorted(alias),
            "predicted_concepts": sorted(prediction),
            "supervised_scores": {
                label: float(score) for label, score in zip(labels, row_scores, strict=True)
            },
        }
        for example, group, fold_id, alias, prediction, row_scores in zip(
            examples,
            groups,
            fold_ids,
            alias_predictions,
            best_predictions,
            scores,
            strict=True,
        )
    ]
    payload = {
        "status": "development_only_assistant_audited_labels",
        "protocol": "paper-disjoint out-of-fold logistic regression over sentence embeddings",
        "datasets": [str(path) for path in args.dataset],
        "label_audits": [str(path) for path in args.label_audit],
        "qasper_data": str(args.qasper_data),
        "folds": len(set(fold_ids)),
        "papers": len(set(groups)),
        "examples": len(examples),
        "label_counts": dict(sorted(label_counts.items())),
        "trained_fold_counts": trained_counts,
        "selection_policy": "highest out-of-fold F1, then precision and exact match",
        "best": best,
        "configurations": configurations,
        "rows": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps({key: payload[key] for key in ("label_counts", "best")}, indent=2))


if __name__ == "__main__":
    main()
