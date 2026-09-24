from collections.abc import Iterable
from typing import TypedDict

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
    items = list(examples)
    results: dict[str, dict[str, float]] = {}
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
        for item, links in zip(items, linked_items, strict=True):
            gold = set(item["gold_concepts"])
            predicted = {link.concept for link in links}
            true_positive += len(predicted.intersection(gold))
            predicted_total += len(predicted)
            gold_total += len(gold)
            exact_matches += int(predicted == gold)

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
    return results
