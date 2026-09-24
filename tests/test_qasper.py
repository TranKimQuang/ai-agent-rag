from app.evaluation.qasper import build_split, convert_qasper_paper, select_qasper_papers
from scripts.prepare_qasper_parquet_subset import parquet_row_to_original


def sample_paper() -> dict[str, object]:
    return {
        "title": "A real scientific paper",
        "full_text": [
            {
                "section_name": "Methods",
                "paragraphs": [
                    "We evaluate the model on QASPER.",
                    "The evidence selector uses paragraph retrieval.",
                ],
            }
        ],
        "qas": [
            {
                "question": "Which dataset is used?",
                "question_id": "q1",
                "answers": [
                    {
                        "answer": {
                            "unanswerable": False,
                            "evidence": ["We evaluate the model on QASPER."],
                        }
                    }
                ],
            },
            {
                "question": "What is not reported?",
                "question_id": "q2",
                "answers": [{"answer": {"unanswerable": True, "evidence": []}}],
            },
        ],
    }


def test_convert_qasper_paper_maps_text_evidence_to_paragraph_chunk() -> None:
    converted = convert_qasper_paper("1234.5678", sample_paper())

    assert len(converted.chunks) == 2
    assert len(converted.questions) == 1
    assert converted.questions[0]["relevant_chunk_ids"] == ["qasper:1234.5678:s0:p0"]


def test_select_and_split_qasper_papers_is_deterministic() -> None:
    payload = {"b": sample_paper(), "a": sample_paper()}

    selected = select_qasper_papers(
        payload,
        paper_limit=2,
        min_questions_per_paper=1,
    )
    split = build_split(selected, split="validation")

    assert [paper.paper_id for paper in selected] == ["a", "b"]
    assert split["metadata"]["paper_ids"] == ["a", "b"]
    assert len(split["questions"]) == 2


def test_select_qasper_papers_excludes_previous_paper_ids() -> None:
    selected = select_qasper_papers(
        {"paper-a": sample_paper(), "paper-b": sample_paper()},
        paper_limit=1,
        min_questions_per_paper=1,
        excluded_paper_ids={"paper-a"},
    )

    assert [paper.paper_id for paper in selected] == ["paper-b"]


def test_parquet_row_is_converted_to_original_qasper_shape() -> None:
    row = {
        "id": "paper-a",
        "title": "Paper A",
        "full_text": {
            "section_name": ["Methods"],
            "paragraphs": [["Evidence paragraph."]],
        },
        "qas": {
            "question": ["What is the evidence?"],
            "question_id": ["q1"],
            "answers": [
                {
                    "answer": [
                        {
                            "unanswerable": False,
                            "evidence": ["Evidence paragraph."],
                        }
                    ]
                }
            ],
        },
    }

    paper_id, paper = parquet_row_to_original(row)
    converted = convert_qasper_paper(paper_id, paper)

    assert paper_id == "paper-a"
    assert converted.questions[0]["relevant_chunk_ids"] == ["qasper:paper-a:s0:p0"]
