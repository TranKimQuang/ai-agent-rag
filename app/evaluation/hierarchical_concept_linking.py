from dataclasses import dataclass
from functools import cache

from app.ontology.service import OntologyService


@dataclass(frozen=True)
class ConceptMatch:
    predicted: str
    gold: str
    credit: float
    relation: str


def concept_match(
    service: OntologyService, predicted: str, gold: str
) -> ConceptMatch | None:
    """Return exact or conservative one-hop taxonomy credit for a concept pair."""
    if predicted == gold:
        return ConceptMatch(predicted, gold, 1.0, "exact")
    if gold in service.broader_concept_names(predicted):
        return ConceptMatch(predicted, gold, 0.5, "predicted_is_narrower")
    if predicted in service.broader_concept_names(gold):
        return ConceptMatch(predicted, gold, 0.5, "predicted_is_broader")
    return None


def best_concept_matches(
    service: OntologyService,
    predicted: set[str],
    gold: set[str],
) -> list[ConceptMatch]:
    """Find deterministic maximum-credit one-to-one matches between two sets."""
    predicted_names = tuple(sorted(predicted))
    gold_names = tuple(sorted(gold))
    candidates = {
        (predicted_index, gold_index): match
        for predicted_index, predicted_name in enumerate(predicted_names)
        for gold_index, gold_name in enumerate(gold_names)
        if (match := concept_match(service, predicted_name, gold_name)) is not None
    }

    @cache
    def solve(predicted_index: int, used_gold_mask: int) -> tuple[ConceptMatch, ...]:
        if predicted_index == len(predicted_names):
            return ()
        best = solve(predicted_index + 1, used_gold_mask)
        for gold_index in range(len(gold_names)):
            if used_gold_mask & (1 << gold_index):
                continue
            match = candidates.get((predicted_index, gold_index))
            if match is None:
                continue
            candidate = (match, *solve(predicted_index + 1, used_gold_mask | (1 << gold_index)))
            if sum(item.credit for item in candidate) > sum(item.credit for item in best):
                best = candidate
        return best

    return list(solve(0, 0))


def score_hierarchical_predictions(
    service: OntologyService,
    gold_sets: list[set[str]],
    predictions: list[set[str]],
) -> dict[str, object]:
    """Report exact metrics and partial-credit one-hop taxonomy metrics."""
    if len(gold_sets) != len(predictions):
        raise ValueError("gold_sets and predictions must have the same length")

    exact_true_positive = 0
    hierarchical_credit = 0.0
    predicted_total = 0
    gold_total = 0
    exact_matches = 0
    partial_matches: list[list[ConceptMatch]] = []
    for gold, predicted in zip(gold_sets, predictions, strict=True):
        matches = best_concept_matches(service, predicted, gold)
        partial_matches.append(matches)
        exact_true_positive += len(predicted & gold)
        hierarchical_credit += sum(match.credit for match in matches)
        predicted_total += len(predicted)
        gold_total += len(gold)
        exact_matches += int(predicted == gold)

    def metrics(true_positive: float) -> dict[str, float]:
        precision = true_positive / predicted_total if predicted_total else 0.0
        recall = true_positive / gold_total if gold_total else 0.0
        f1 = (
            2 * precision * recall / (precision + recall)
            if precision + recall
            else 0.0
        )
        return {"precision": precision, "recall": recall, "f1": f1}

    return {
        "exact": {
            **metrics(float(exact_true_positive)),
            "exact_match": exact_matches / len(gold_sets) if gold_sets else 0.0,
        },
        "taxonomy_aware": metrics(hierarchical_credit),
        "counts": {
            "examples": len(gold_sets),
            "predicted": predicted_total,
            "gold": gold_total,
            "exact_true_positive": exact_true_positive,
            "taxonomy_credit": hierarchical_credit,
        },
        "matches": partial_matches,
    }
