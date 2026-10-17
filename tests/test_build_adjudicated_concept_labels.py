import json

from scripts.build_adjudicated_concept_labels import build_adjudicated_labels


def test_build_adjudicated_labels_applies_exact_disagreement_decisions(tmp_path) -> None:
    dataset = tmp_path / "dataset.json"
    reference = tmp_path / "reference.json"
    reconciliation = tmp_path / "reconciliation.json"
    adjudication = tmp_path / "adjudication.json"
    dataset.write_text(
        json.dumps(
            [
                {
                    "source_question_id": "q1",
                    "text": "How is BERT different?",
                    "gold_concepts": [],
                }
            ]
        ),
        encoding="utf-8",
    )
    reference.write_text(
        json.dumps(
            {
                "items": [
                    {
                        "review_id": "CR-001",
                        "source_question_id": "q1",
                        "audited_concepts": [],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    reconciliation.write_text(
        json.dumps({"disagreements": [{"review_id": "CR-001"}]}),
        encoding="utf-8",
    )
    adjudication.write_text(
        json.dumps(
            {
                "adjudications": [
                    {
                        "review_id": "CR-001",
                        "adjudicated_concepts": ["BidirectionalLanguageModel"],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    result = build_adjudicated_labels(
        [dataset],
        [],
        reference,
        reconciliation,
        adjudication,
        {"BidirectionalLanguageModel"},
    )

    assert result[0]["gold_concepts"] == ["BidirectionalLanguageModel"]
    assert result[0]["review_status"] == "llm_adjudicated_not_human_gold"
