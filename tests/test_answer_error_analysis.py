from app.models import SearchMethod, SearchResult
from scripts.analyze_qasper_answer_errors import classify_case


def result(chunk_id: str) -> SearchResult:
    return SearchResult(
        chunk_id=chunk_id,
        document_id="paper",
        filename="paper.json",
        page=1,
        text="Evidence.",
        method=SearchMethod.HYBRID_ONTOLOGY_RERANK,
        score=1.0,
    )


def row(**updates):
    value = {
        "expected_kind": "answerable",
        "agent_status": "answered",
        "answer_f1": 0.8,
        "evidence_f1": 1.0,
        "references": [{"evidence_chunk_ids": ["gold"]}],
    }
    value.update(updates)
    return value


def test_error_analysis_separates_retrieval_gate_answer_and_citation() -> None:
    assert classify_case(row(), [result("other")])[0] == "retrieval_miss_with_answer"
    assert (
        classify_case(
            row(agent_status="insufficient_evidence"), [result("gold")]
        )[0]
        == "gate_false_rejection"
    )
    assert (
        classify_case(row(evidence_f1=0.0), [result("gold")])[0]
        == "citation_selection_error"
    )
    assert (
        classify_case(row(answer_f1=0.2), [result("gold")])[0]
        == "answer_content_or_format_error"
    )
    assert classify_case(row(), [result("gold")])[0] == "successful_answer"


def test_error_analysis_recognizes_correct_unanswerable_refusal() -> None:
    category, rank = classify_case(
        row(expected_kind="unanswerable", agent_status="insufficient_evidence"),
        [],
    )

    assert category == "correct_unanswerable_refusal"
    assert rank is None
