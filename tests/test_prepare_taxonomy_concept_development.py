import json
from pathlib import Path

from app.evaluation.qasper import QasperPaperBenchmark
from app.models import Chunk
from app.ontology.service import OntologyService
from scripts.prepare_taxonomy_concept_development import (
    collect_excluded_question_ids,
    select_taxonomy_questions,
    taxonomy_concepts,
)


def paper(paper_id: str, questions: list[tuple[str, str]]) -> QasperPaperBenchmark:
    return QasperPaperBenchmark(
        paper_id=paper_id,
        title="Test",
        abstract="",
        chunks=[
            Chunk(
                id=f"qasper:{paper_id}:s0:p0",
                document_id=paper_id,
                filename=f"qasper-{paper_id}.json",
                page=1,
                text="Evidence",
            )
        ],
        questions=[
            {
                "id": question_id,
                "query": query,
                "relevant_chunk_ids": [f"qasper:{paper_id}:s0:p0"],
                "category": "qasper_real",
                "paper_id": paper_id,
            }
            for question_id, query in questions
        ],
    )


def test_taxonomy_concepts_include_direct_children_and_parents() -> None:
    concepts = taxonomy_concepts(OntologyService())

    assert "MachineReadingComprehension" in concepts
    assert "QuestionAnswering" in concepts


def test_selection_keeps_only_explicit_taxonomy_candidates() -> None:
    papers, strata = select_taxonomy_questions(
        [
            paper(
                "p1",
                [
                    ("q1", "How does machine reading comprehension work?"),
                    ("q2", "Which dataset was used?"),
                ],
            )
        ],
        OntologyService(),
        per_concept=3,
        max_questions=10,
        max_questions_per_paper=3,
        seed=7,
    )

    assert [question["id"] for question in papers[0].questions] == ["q1"]
    assert strata == {"q1": ["MachineReadingComprehension"]}


def test_selection_respects_per_paper_limit() -> None:
    papers, _ = select_taxonomy_questions(
        [
            paper(
                "p1",
                [
                    ("q1", "Is question answering evaluated?"),
                    ("q2", "Does question answering use retrieval?"),
                ],
            )
        ],
        OntologyService(),
        per_concept=5,
        max_questions=10,
        max_questions_per_paper=1,
        seed=11,
    )

    assert len(papers) == 1
    assert len(papers[0].questions) == 1


def test_collect_excluded_question_ids(tmp_path: Path) -> None:
    dataset = tmp_path / "dataset.json"
    dataset.write_text(
        json.dumps({"questions": [{"id": "q1"}, {"id": "q2"}]}),
        encoding="utf-8",
    )

    assert collect_excluded_question_ids([dataset]) == {"q1", "q2"}
