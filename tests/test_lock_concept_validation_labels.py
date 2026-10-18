import pytest

from scripts.lock_concept_validation_labels import build_locked_labels


def test_build_locked_labels_validates_and_preserves_packet_order() -> None:
    packet = [
        {
            "review_id": "CV-001",
            "source_question_id": "q1",
            "question": "Question one?",
        },
        {
            "review_id": "CV-002",
            "source_question_id": "q2",
            "question": "Question two?",
        },
    ]
    labels = [
        {"review_id": "CV-002", "reviewer_concepts": "", "reviewer_none": "1"},
        {
            "review_id": "CV-001",
            "reviewer_concepts": "SemanticSearch|InformationRetrieval",
            "reviewer_none": "0",
        },
    ]

    locked, summary = build_locked_labels(
        packet,
        labels,
        {"InformationRetrieval", "SemanticSearch"},
    )

    assert [row["source_question_id"] for row in locked] == ["q1", "q2"]
    assert locked[0]["gold_concepts"] == [
        "InformationRetrieval",
        "SemanticSearch",
    ]
    assert locked[1]["gold_concepts"] == []
    assert summary == {
        "questions": 2,
        "positive_questions": 1,
        "none_questions": 1,
        "concept_assignments": 2,
    }


def test_build_locked_labels_rejects_unknown_concept() -> None:
    packet = [
        {"review_id": "CV-001", "source_question_id": "q1", "question": "Q?"}
    ]
    labels = [
        {"review_id": "CV-001", "reviewer_concepts": "Unknown", "reviewer_none": "0"}
    ]

    with pytest.raises(ValueError, match="unknown concepts"):
        build_locked_labels(packet, labels, {"SemanticSearch"})

