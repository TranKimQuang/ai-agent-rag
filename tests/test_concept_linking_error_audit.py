from scripts.audit_concept_linking_errors import classify_coverage_row
from scripts.suggest_concept_labels import (
    ConceptLabelSuggestion,
    constrain_suggestion,
    validate_allowed_concepts,
)


def row(
    query_concepts: list[str],
    gold_concepts: list[str],
    *,
    related: bool = False,
) -> dict[str, object]:
    return {
        "query_concepts": query_concepts,
        "gold_concepts": gold_concepts,
        "gold_has_ontology_relation": related,
    }


def test_classify_coverage_row_separates_actionable_failure_groups() -> None:
    assert classify_coverage_row(row([], [])) == "missing_query_and_gold_concepts"
    assert classify_coverage_row(row([], ["A"])) == "missing_query_concept"
    assert classify_coverage_row(row(["A"], [])) == "missing_gold_concept"
    assert (
        classify_coverage_row(row(["A"], ["B"]))
        == "missing_relation_or_query_mismatch"
    )
    assert classify_coverage_row(row(["A"], ["B"], related=True)) == "useful_relation"


def test_provisional_label_rejects_concepts_outside_supplied_candidates() -> None:
    suggestion = ConceptLabelSuggestion(
        question_id="q1",
        query_concepts=["Invented"],
        evidence_concepts=[],
        relation="none",
        confidence=0.8,
        rationale="The invented label is not allowed.",
    )
    try:
        validate_allowed_concepts(
            suggestion,
            query_allowed={"Known"},
            evidence_allowed={"Evidence"},
        )
    except ValueError as exc:
        assert "outside" in str(exc)
    else:
        raise AssertionError("Expected an invalid candidate to be rejected")


def test_provisional_label_constrains_invented_concepts_and_lowers_confidence() -> None:
    suggestion = ConceptLabelSuggestion(
        question_id="q1",
        query_concepts=["Known", "Invented"],
        evidence_concepts=["MadeUp"],
        relation="related",
        confidence=0.9,
        rationale="The model selected an extra label.",
    )
    adjusted = constrain_suggestion(
        suggestion,
        query_allowed={"Known"},
        evidence_allowed={"Evidence"},
    )
    assert adjusted.query_concepts == ["Known"]
    assert adjusted.evidence_concepts == []
    assert adjusted.relation == "uncertain"
    assert adjusted.confidence == 0.5
    assert adjusted.rationale.startswith("Constraint adjusted")
