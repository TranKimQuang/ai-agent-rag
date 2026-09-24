import re
from dataclasses import dataclass

from app.models import Chunk

_WHITESPACE = re.compile(r"\s+")


def normalize_evidence(text: str) -> str:
    return _WHITESPACE.sub(" ", text).strip()


@dataclass(frozen=True)
class QasperPaperBenchmark:
    paper_id: str
    title: str
    chunks: list[Chunk]
    questions: list[dict[str, object]]


def convert_qasper_paper(
    paper_id: str,
    paper: dict[str, object],
    *,
    max_questions: int = 5,
) -> QasperPaperBenchmark:
    """Convert one official QASPER paper into paragraph-level retrieval gold data."""
    chunks: list[Chunk] = []
    evidence_lookup: dict[str, str] = {}
    paragraph_number = 0
    for section_index, section in enumerate(paper["full_text"]):  # type: ignore[union-attr]
        section_name = str(section.get("section_name", ""))
        for paragraph_index, paragraph in enumerate(section.get("paragraphs", [])):
            text = normalize_evidence(str(paragraph))
            if not text:
                continue
            paragraph_number += 1
            chunk_id = f"qasper:{paper_id}:s{section_index}:p{paragraph_index}"
            chunk_text = f"{section_name}. {text}" if section_name else text
            chunks.append(
                Chunk(
                    id=chunk_id,
                    document_id=paper_id,
                    filename=f"qasper-{paper_id}.json",
                    page=paragraph_number,
                    text=chunk_text,
                )
            )
            evidence_lookup.setdefault(text, chunk_id)

    questions: list[dict[str, object]] = []
    for qa in paper["qas"]:  # type: ignore[union-attr]
        relevant_ids: set[str] = set()
        for annotation in qa.get("answers", []):
            answer = annotation.get("answer", {})
            if answer.get("unanswerable"):
                continue
            for evidence in answer.get("evidence", []):
                evidence_text = str(evidence)
                if evidence_text.startswith("FLOAT SELECTED"):
                    continue
                chunk_id = evidence_lookup.get(normalize_evidence(evidence_text))
                if chunk_id:
                    relevant_ids.add(chunk_id)

        if not relevant_ids:
            continue
        questions.append(
            {
                "id": str(qa["question_id"]),
                "query": str(qa["question"]),
                "relevant_chunk_ids": sorted(relevant_ids),
                "category": "qasper_real",
                "paper_id": paper_id,
            }
        )
        if len(questions) >= max_questions:
            break

    return QasperPaperBenchmark(
        paper_id=paper_id,
        title=str(paper["title"]),
        chunks=chunks,
        questions=questions,
    )


def select_qasper_papers(
    payload: dict[str, dict[str, object]],
    *,
    paper_limit: int = 20,
    min_questions_per_paper: int = 3,
    max_questions_per_paper: int = 5,
    excluded_paper_ids: set[str] | None = None,
) -> list[QasperPaperBenchmark]:
    selected: list[QasperPaperBenchmark] = []
    excluded = excluded_paper_ids or set()
    for paper_id in sorted(payload):
        if paper_id in excluded:
            continue
        converted = convert_qasper_paper(
            paper_id,
            payload[paper_id],
            max_questions=max_questions_per_paper,
        )
        if len(converted.questions) < min_questions_per_paper:
            continue
        selected.append(converted)
        if len(selected) >= paper_limit:
            break
    return selected


def build_split(
    papers: list[QasperPaperBenchmark],
    *,
    split: str,
) -> dict[str, object]:
    return {
        "metadata": {
            "dataset": "QASPER",
            "version": "0.3",
            "split": split,
            "license": "CC BY 4.0",
            "source": "https://allenai.org/data/qasper",
            "paper_ids": [paper.paper_id for paper in papers],
            "locator_note": (
                "Chunk page stores the one-based paragraph ordinal because the official "
                "QASPER JSON does not provide PDF page numbers."
            ),
        },
        "chunks": [chunk.model_dump() for paper in papers for chunk in paper.chunks],
        "questions": [question for paper in papers for question in paper.questions],
    }
