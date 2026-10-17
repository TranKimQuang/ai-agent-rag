from collections.abc import Iterable
from typing import Any, TypedDict

from app.models import ConceptLinkingMethod
from app.ontology.service import OntologyService


class ConceptLinkingExample(TypedDict):
    text: str
    gold_concepts: list[str]


def evaluate_concept_linking(
    service: OntologyService,
    examples: Iterable[ConceptLinkingExample],
    *,
    threshold: float = 0.55,
) -> dict[str, dict[str, float]]:
    """Compare alias, semantic, and hybrid concept linking on labelled text."""
    return evaluate_concept_linking_with_rows(
        service,
        examples,
        threshold=threshold,
    )["results"]


def evaluate_concept_linking_with_rows(
    service: OntologyService,
    examples: Iterable[ConceptLinkingExample],
    *,
    threshold: float = 0.55,
) -> dict[str, Any]:
    """Evaluate all methods and retain per-question predictions in the same run."""
    items = list(examples)
    results: dict[str, dict[str, float]] = {}
    rows: list[dict[str, Any]] = [
        {
            "source_question_id": item.get("source_question_id"),
            "text": item["text"],
            "gold_concepts": item["gold_concepts"],
            "predictions": {},
        }
        for item in items
    ]
    for method in ConceptLinkingMethod:
        true_positive = 0
        predicted_total = 0
        gold_total = 0
        exact_matches = 0
        linked_items = service.link_concepts_batch(
            [item["text"] for item in items],
            method,
            threshold=threshold,
            limit=20,
        )
        for item, links, row in zip(items, linked_items, rows, strict=True):
            gold = set(item["gold_concepts"])
            predicted = {link.concept for link in links}
            true_positive += len(predicted.intersection(gold))
            predicted_total += len(predicted)
            gold_total += len(gold)
            exact_matches += int(predicted == gold)
            row["predictions"][method.value] = {
                "concepts": sorted(predicted),
                "links": [link.model_dump(mode="json") for link in links],
            }

        precision = true_positive / predicted_total if predicted_total else 0.0
        recall = true_positive / gold_total if gold_total else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        results[method.value] = {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "exact_match": exact_matches / len(items) if items else 0.0,
            "examples": float(len(items)),
        }
    return {"results": results, "rows": rows}
