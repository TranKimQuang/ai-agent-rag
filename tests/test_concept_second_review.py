import json

from scripts.prepare_concept_second_review import build_review_rows


def test_second_review_packet_is_blinded_and_keeps_key_separate(tmp_path) -> None:
    dataset = tmp_path / "dataset.json"
    audit = tmp_path / "audit.json"
    evidence = tmp_path / "evidence.json"
    dataset.write_text(
        json.dumps(
            [
                {
                    "source_question_id": "q1",
                    "text": "Does it use embeddings?",
                    "gold_concepts": ["WordEmbedding"],
                }
            ]
        ),
        encoding="utf-8",
    )
    audit.write_text(
        json.dumps(
            {
                "corrections": [
                    {"source_question_id": "q1", "audited_concepts": []}
                ]
            }
        ),
        encoding="utf-8",
    )
    evidence.write_text(
        json.dumps(
            {
                "questions": [
                    {
                        "question_id": "q1",
                        "document_id": "paper-1",
                        "gold_evidence_excerpt": "Evidence text.",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    rows, keys = build_review_rows([dataset], [audit], evidence)

    assert rows[0]["reviewer_concepts"] == ""
    assert "WordEmbedding" not in str(rows[0])
    assert keys[0]["audited_concepts"] == []
    assert keys[0]["source_question_id"] == "q1"
