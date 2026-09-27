"""QASPER answer and evidence helpers adapted from the official evaluator."""

import re
import string
from collections import Counter
from dataclasses import dataclass

from app.evaluation.qasper import normalize_evidence


@dataclass(frozen=True)
class QasperReference:
    answer: str
    answer_type: str
    evidence_chunk_ids: list[str]


def paragraph_chunk_lookup(
    paper_id: str, paper: dict[str, object]
) -> dict[str, str]:
    lookup: dict[str, str] = {}
    for section_index, section in enumerate(paper["full_text"]):  # type: ignore[union-attr]
        for paragraph_index, paragraph in enumerate(section.get("paragraphs", [])):
            text = normalize_evidence(str(paragraph))
            if text:
                lookup.setdefault(
                    text,
                    f"qasper:{paper_id}:s{section_index}:p{paragraph_index}",
                )
    return lookup


def answer_text(answer: dict[str, object]) -> tuple[str, str]:
    if answer.get("unanswerable"):
        return "Unanswerable", "none"
    spans = [str(value) for value in answer.get("extractive_spans", [])]
    if spans:
        return ", ".join(spans), "extractive"
    free_form = str(answer.get("free_form_answer") or "").strip()
    if free_form:
        return free_form, "abstractive"
    yes_no = answer.get("yes_no")
    if yes_no is True:
        return "Yes", "boolean"
    if yes_no is False:
        return "No", "boolean"
    raise ValueError("QASPER annotation does not contain a supported answer")


def question_references(
    paper_id: str,
    paper: dict[str, object],
    qa: dict[str, object],
) -> list[QasperReference]:
    lookup = paragraph_chunk_lookup(paper_id, paper)
    references = []
    for annotation in qa.get("answers", []):
        answer = annotation.get("answer", {})
        text, answer_type = answer_text(answer)
        evidence_ids = []
        if answer_type != "none":
            for evidence in answer.get("evidence", []):
                evidence_text = str(evidence)
                if evidence_text.startswith("FLOAT SELECTED"):
                    continue
                chunk_id = lookup.get(normalize_evidence(evidence_text))
                if chunk_id and chunk_id not in evidence_ids:
                    evidence_ids.append(chunk_id)
        references.append(QasperReference(text, answer_type, evidence_ids))
    return references


def normalize_answer(text: str) -> str:
    lowered = text.lower()
    without_punctuation = "".join(
        character for character in lowered if character not in set(string.punctuation)
    )
    without_articles = re.sub(r"\b(a|an|the)\b", " ", without_punctuation)
    return " ".join(without_articles.split())


def token_f1(prediction: str, reference: str) -> float:
    prediction_tokens = normalize_answer(prediction).split()
    reference_tokens = normalize_answer(reference).split()
    common = Counter(prediction_tokens) & Counter(reference_tokens)
    matches = sum(common.values())
    if matches == 0:
        return 0.0
    precision = matches / len(prediction_tokens)
    recall = matches / len(reference_tokens)
    return 2 * precision * recall / (precision + recall)


def evidence_f1(prediction: list[str], reference: list[str]) -> float:
    if not prediction and not reference:
        return 1.0
    matches = len(set(prediction).intersection(reference))
    if matches == 0:
        return 0.0
    precision = matches / len(set(prediction))
    recall = matches / len(set(reference))
    return 2 * precision * recall / (precision + recall)
