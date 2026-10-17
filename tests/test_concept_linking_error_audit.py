from scripts.audit_concept_linking_errors import classify_coverage_row


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
