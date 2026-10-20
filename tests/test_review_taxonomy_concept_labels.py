from pathlib import Path

import pytest
from pydantic import ValidationError

from scripts.review_taxonomy_concept_labels import (
    TaxonomyLabel,
    constrain_to_catalog,
    write_labels_csv,
)


def test_taxonomy_label_requires_concepts_xor_none() -> None:
    with pytest.raises(ValidationError):
        TaxonomyLabel(
            review_id="CV-001",
            concepts=[],
            none=False,
            confidence=0.9,
            rationale="Missing decision",
        )


def test_taxonomy_label_csv_matches_locking_schema(tmp_path: Path) -> None:
    output = tmp_path / "labels.csv"
    write_labels_csv(
        output,
        [
            TaxonomyLabel(
                review_id="CV-001",
                concepts=["QuestionAnswering"],
                none=False,
                confidence=0.95,
                rationale="QA is explicit.",
            ),
            TaxonomyLabel(
                review_id="CV-002",
                concepts=[],
                none=True,
                confidence=0.8,
                rationale="No catalog topic is explicit.",
            ),
        ],
    )

    content = output.read_text(encoding="utf-8-sig")
    assert "CV-001,QuestionAnswering,0" in content
    assert "CV-002,,1" in content


def test_unknown_concept_is_removed_and_flagged_for_audit() -> None:
    constrained = constrain_to_catalog(
        TaxonomyLabel(
            review_id="CV-001",
            concepts=["InventedConcept"],
            none=False,
            confidence=0.95,
            rationale="Model proposal.",
        ),
        {"QuestionAnswering"},
    )

    assert constrained.concepts == []
    assert constrained.none is True
    assert constrained.confidence == 0.5
    assert constrained.rationale.startswith("Constraint adjusted")
