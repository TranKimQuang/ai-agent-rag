import pytest

from scripts.reconcile_concept_second_review import parse_reviewer_labels, reconcile


def test_reconcile_reports_exact_agreement_and_disagreements() -> None:
    rows = [
        {
            "review_id": "CR-001",
            "question": "Question one",
            "reviewer_concepts": "WordEmbedding",
            "reviewer_none": "",
            "reviewer_notes": "",
        },
        {
            "review_id": "CR-002",
            "question": "Question two",
            "reviewer_concepts": "",
            "reviewer_none": "X",
            "reviewer_notes": "No concept",
        },
    ]
    key = [
        {
            "review_id": "CR-001",
            "source_question_id": "q1",
            "audited_concepts": ["WordEmbedding"],
        },
        {
            "review_id": "CR-002",
            "source_question_id": "q2",
            "audited_concepts": ["SemanticSearch"],
        },
    ]

    result = reconcile(rows, key, {"WordEmbedding", "SemanticSearch"})

    assert result["exact_agreement"] == 0.5
    assert result["disagreement_count"] == 1
    assert result["status"] == "requires_disagreement_resolution"


@pytest.mark.parametrize(
    ("concepts", "none"), [("", ""), ("WordEmbedding", "X")]
)
def test_reviewer_must_fill_exactly_one_label_field(concepts: str, none: str) -> None:
    with pytest.raises(ValueError, match="not both/neither"):
        parse_reviewer_labels(
            {
                "review_id": "CR-001",
                "reviewer_concepts": concepts,
                "reviewer_none": none,
            },
            {"WordEmbedding"},
        )


def test_reviewer_cannot_invent_concept() -> None:
    with pytest.raises(ValueError, match="unknown concepts"):
        parse_reviewer_labels(
            {
                "review_id": "CR-001",
                "reviewer_concepts": "InventedConcept",
                "reviewer_none": "",
            },
            {"WordEmbedding"},
        )
