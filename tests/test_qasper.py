from app.evaluation.qasper import build_split, convert_qasper_paper, select_qasper_papers
from app.evaluation.qasper_answers import (
    answer_text,
    evidence_f1,
    question_references,
    token_f1,
)
from app.evaluation.qasper_protocol import (
    serialize_split,
    sha256_bytes,
    split_protocol_papers,
)
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
                            "extractive_spans": ["QASPER"],
                            "free_form_answer": "",
                            "yes_no": None,
                            "evidence": ["We evaluate the model on QASPER."],
                        }
                    }
                ],
            },
            {
                "question": "What is not reported?",
                "question_id": "q2",
                "answers": [
                    {
                        "answer": {
                            "unanswerable": True,
                            "extractive_spans": [],
                            "free_form_answer": "",
                            "yes_no": None,
                            "evidence": [],
                        }
                    }
                ],
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


def test_seeded_qasper_selection_is_deterministic() -> None:
    payload = {str(index): sample_paper() for index in range(8)}

    first = select_qasper_papers(
        payload,
        paper_limit=4,
        min_questions_per_paper=1,
        selection_seed=17,
    )
    second = select_qasper_papers(
        payload,
        paper_limit=4,
        min_questions_per_paper=1,
        selection_seed=17,
    )

    assert [paper.paper_id for paper in first] == [paper.paper_id for paper in second]
    assert [paper.paper_id for paper in first] != sorted(paper.paper_id for paper in first)


def test_protocol_splits_are_disjoint_and_hashable() -> None:
    payload = {str(index): sample_paper() for index in range(6)}
    selected = select_qasper_papers(
        payload,
        paper_limit=6,
        min_questions_per_paper=1,
        selection_seed=19,
    )

    splits = split_protocol_papers(
        selected,
        development_papers=2,
        validation_papers=2,
        final_test_papers=2,
    )
    ids = {
        name: {paper.paper_id for paper in papers}
        for name, papers in splits.items()
    }

    assert ids["development"].isdisjoint(ids["validation"])
    assert ids["development"].isdisjoint(ids["final_test"])
    assert ids["validation"].isdisjoint(ids["final_test"])
    content = serialize_split(splits["final_test"], split="sealed")
    assert len(sha256_bytes(content)) == 64


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


def test_qasper_answer_helpers_match_answer_and_evidence() -> None:
    paper = sample_paper()
    qa = paper["qas"][0]

    references = question_references("1234.5678", paper, qa)

    assert references[0].answer == "QASPER"
    assert references[0].answer_type == "extractive"
    assert references[0].evidence_chunk_ids == ["qasper:1234.5678:s0:p0"]
    assert token_f1("The QASPER.", "QASPER") == 1.0
    assert evidence_f1(["a", "b"], ["b", "c"]) == 0.5


def test_qasper_answer_types_follow_official_priority() -> None:
    assert answer_text({"unanswerable": True}) == ("Unanswerable", "none")
    assert answer_text({"extractive_spans": ["one", "two"]}) == (
        "one, two",
        "extractive",
    )
    assert answer_text({"free_form_answer": "summary"}) == (
        "summary",
        "abstractive",
    )
    assert answer_text({"yes_no": True}) == ("Yes", "boolean")
    assert answer_text({"yes_no": False}) == ("No", "boolean")
