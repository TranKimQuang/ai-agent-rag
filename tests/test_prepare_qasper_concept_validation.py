from scripts.prepare_qasper_concept_validation import build_blinded_review_rows


def test_blinded_review_rows_include_gold_evidence_without_predictions() -> None:
    dataset = {
        "chunks": [
            {"id": "c1", "text": "First gold passage."},
            {"id": "c2", "text": "Second gold passage."},
        ],
        "questions": [
            {
                "id": "q1",
                "paper_id": "p1",
                "query": "Which method is used?",
                "relevant_chunk_ids": ["c1", "c2"],
            }
        ],
    }

    rows = build_blinded_review_rows(dataset)

    assert rows == [
        {
            "review_id": "CV-001",
            "source_question_id": "q1",
            "paper_id": "p1",
            "question": "Which method is used?",
            "gold_evidence_excerpt": (
                "First gold passage. || Second gold passage."
            ),
            "reviewer_concepts": "",
            "reviewer_none": "",
            "reviewer_notes": "",
        }
    ]
    assert not any("prediction" in key for key in rows[0])

