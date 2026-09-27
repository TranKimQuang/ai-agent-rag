"""Evaluate the local Agent on answerable and naturally unanswerable QASPER questions."""

import argparse
import json
import re
import time
from datetime import UTC, datetime
from pathlib import Path
from statistics import mean

from app.agent.ollama import GenerationError, OllamaAnswerGenerator
from app.agent.service import DocumentQuestionAgent
from app.evaluation.qasper_answers import (
    QasperReference,
    evidence_f1,
    question_references,
    token_f1,
)
from app.models import AgentStatus, Chunk, ConceptLinkingMethod, SearchMethod
from app.ontology.service import OntologyService
from app.rag.reranker import SentenceTransformerCrossEncoderReranker
from app.rag.retriever import InMemoryHybridRetriever, SentenceTransformerEncoder

DEFAULT_RETRIEVAL_DATASET = Path(
    "evaluation/qasper_train_v3/qasper_train_development.json"
)
_CITATION_MARKER = re.compile(r"\s*\[\d+\]")


def select_distinct_papers(
    items: list[dict[str, object]], limit: int
) -> list[dict[str, object]]:
    selected: list[dict[str, object]] = []
    selected_ids: set[str] = set()
    seen_papers: set[str] = set()
    for item in items:
        paper_id = str(item["paper_id"])
        if paper_id in seen_papers:
            continue
        selected.append(item)
        selected_ids.add(str(item["id"]))
        seen_papers.add(paper_id)
        if len(selected) == limit:
            return selected
    for item in items:
        if str(item["id"]) in selected_ids:
            continue
        selected.append(item)
        if len(selected) == limit:
            break
    return selected


def reference_payload(references: list[QasperReference]) -> list[dict[str, object]]:
    return [
        {
            "answer": reference.answer,
            "answer_type": reference.answer_type,
            "evidence_chunk_ids": reference.evidence_chunk_ids,
        }
        for reference in references
    ]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Development-only answer and citation evaluation with local Ollama"
    )
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument(
        "--retrieval-dataset", type=Path, default=DEFAULT_RETRIEVAL_DATASET
    )
    parser.add_argument("--answerable", type=int, default=20)
    parser.add_argument("--unanswerable", type=int, default=5)
    parser.add_argument(
        "--question-id",
        action="append",
        default=[],
        help="Run only a specific development question ID; may be repeated.",
    )
    parser.add_argument("--model", default="qwen3:4b")
    parser.add_argument(
        "--retrieval-method",
        type=SearchMethod,
        choices=[
            SearchMethod.HYBRID_ONTOLOGY_RERANK,
            SearchMethod.HYBRID_ONTOLOGY_CROSS_ENCODER,
        ],
        default=SearchMethod.HYBRID_ONTOLOGY_RERANK,
    )
    parser.add_argument(
        "--reranker-model", default="cross-encoder/ms-marco-MiniLM-L6-v2"
    )
    parser.add_argument("--reranker-device", default="cpu")
    parser.add_argument("--output-dir", type=Path, default=Path("results"))
    args = parser.parse_args()
    if args.answerable < 1 or args.unanswerable < 1:
        parser.error("answerable and unanswerable counts must be positive")

    retrieval_data = json.loads(args.retrieval_dataset.read_text(encoding="utf-8"))
    split_name = str(retrieval_data.get("metadata", {}).get("split", ""))
    if "heldout" in split_name.lower():
        raise ValueError("Answer development evaluation must not use held-out data")
    source_data = json.loads(args.source.read_text(encoding="utf-8"))
    paper_ids = {str(value) for value in retrieval_data["metadata"]["paper_ids"]}
    source_papers = {
        paper_id: source_data[paper_id]
        for paper_id in paper_ids
        if paper_id in source_data
    }
    if set(source_papers) != paper_ids:
        missing = sorted(paper_ids.difference(source_papers))
        raise ValueError(f"Official QASPER source is missing papers: {missing}")

    answerable_candidates = retrieval_data["questions"]
    selected_answerable = select_distinct_papers(
        answerable_candidates, args.answerable
    )
    unanswerable_candidates: list[dict[str, object]] = []
    for paper_id in sorted(source_papers):
        paper = source_papers[paper_id]
        for qa in paper["qas"]:
            references = question_references(paper_id, paper, qa)
            if references and all(ref.answer_type == "none" for ref in references):
                unanswerable_candidates.append(
                    {
                        "id": str(qa["question_id"]),
                        "query": str(qa["question"]),
                        "paper_id": paper_id,
                    }
                )
    selected_unanswerable = select_distinct_papers(
        unanswerable_candidates, args.unanswerable
    )
    all_answerable = [
        {**item, "expected_kind": "answerable"} for item in answerable_candidates
    ]
    all_unanswerable = [
        {**item, "expected_kind": "unanswerable"}
        for item in selected_unanswerable
    ]
    if args.question_id:
        candidates_by_id = {
            str(item["id"]): item
            for item in [
                *all_answerable,
                *[
                    {**item, "expected_kind": "unanswerable"}
                    for item in unanswerable_candidates
                ],
            ]
        }
        missing = [value for value in args.question_id if value not in candidates_by_id]
        if missing:
            raise ValueError(f"Unknown development question IDs: {missing}")
        selected = [candidates_by_id[value] for value in args.question_id]
    else:
        selected = [
            {**item, "expected_kind": "answerable"} for item in selected_answerable
        ] + all_unanswerable

    encoder = SentenceTransformerEncoder()
    ontology = OntologyService(
        semantic_encoder=encoder,
        linking_method=ConceptLinkingMethod.HYBRID,
        linking_threshold=0.65,
    )
    chunks = [Chunk.model_validate(item) for item in retrieval_data["chunks"]]
    chunks, concept_links = ontology.index_chunks(chunks)
    retriever = InMemoryHybridRetriever(
        semantic_encoder=encoder,
        ontology_service=ontology,
        cross_encoder_reranker=(
            SentenceTransformerCrossEncoderReranker(
                args.reranker_model,
                device=args.reranker_device,
            )
            if args.retrieval_method
            == SearchMethod.HYBRID_ONTOLOGY_CROSS_ENCODER
            else None
        ),
    )
    retriever.add(chunks)
    agent = DocumentQuestionAgent(
        retriever,
        answer_generator=OllamaAnswerGenerator(args.model),
        retrieval_method=args.retrieval_method,
    )

    qa_lookup = {
        (paper_id, str(qa["question_id"])): qa
        for paper_id, paper in source_papers.items()
        for qa in paper["qas"]
    }
    rows: list[dict[str, object]] = []
    for number, item in enumerate(selected, start=1):
        paper_id = str(item["paper_id"])
        question_id = str(item["id"])
        question = str(item["query"])
        qa = qa_lookup[(paper_id, question_id)]
        references = question_references(paper_id, source_papers[paper_id], qa)
        started = time.perf_counter()
        try:
            response = agent.ask(question, limit=5, document_id=paper_id)
            error = None
        except GenerationError as exc:
            response = None
            error = str(exc)
        elapsed = time.perf_counter() - started

        if response is None:
            prediction = ""
            citation_ids: list[str] = []
            status = "generation_error"
        else:
            status = response.status.value
            prediction = (
                "Unanswerable"
                if response.status == AgentStatus.INSUFFICIENT_EVIDENCE
                else _CITATION_MARKER.sub("", response.answer).strip()
            )
            citation_ids = list(dict.fromkeys(c.chunk_id for c in response.citations))
        answer_scores = [token_f1(prediction, ref.answer) for ref in references]
        evidence_scores = [
            evidence_f1(citation_ids, ref.evidence_chunk_ids) for ref in references
        ]
        best_answer_f1 = max(answer_scores, default=0.0)
        best_evidence_f1 = max(evidence_scores, default=0.0)
        gold_evidence = sorted(
            {
                chunk_id
                for reference in references
                for chunk_id in reference.evidence_chunk_ids
            }
        )
        overlap = set(citation_ids).intersection(gold_evidence)
        citation_precision = len(overlap) / len(citation_ids) if citation_ids else (
            1.0 if not gold_evidence else 0.0
        )
        citation_recall = len(overlap) / len(gold_evidence) if gold_evidence else (
            1.0 if not citation_ids else 0.0
        )
        row = {
            "question_id": question_id,
            "paper_id": paper_id,
            "question": question,
            "expected_kind": item["expected_kind"],
            "references": reference_payload(references),
            "agent_status": status,
            "prediction": prediction,
            "citation_chunk_ids": citation_ids,
            "answer_f1": best_answer_f1,
            "evidence_f1": best_evidence_f1,
            "citation_precision": citation_precision,
            "citation_recall": citation_recall,
            "elapsed_seconds": round(elapsed, 3),
            "error": error,
            "trace": (
                [step.model_dump(mode="json") for step in response.trace]
                if response
                else []
            ),
        }
        rows.append(row)
        print(
            json.dumps(
                {
                    "case": f"{number}/{len(selected)}",
                    "kind": item["expected_kind"],
                    "status": status,
                    "answer_f1": round(best_answer_f1, 4),
                    "evidence_f1": round(best_evidence_f1, 4),
                    "elapsed_seconds": row["elapsed_seconds"],
                }
            ),
            flush=True,
        )

    answerable_rows = [row for row in rows if row["expected_kind"] == "answerable"]
    unanswerable_rows = [
        row for row in rows if row["expected_kind"] == "unanswerable"
    ]
    summary = {
        "questions": len(rows),
        "answerable_questions": len(answerable_rows),
        "unanswerable_questions": len(unanswerable_rows),
        "requested_unanswerable_questions": args.unanswerable,
        "answer_f1": mean(float(row["answer_f1"]) for row in rows),
        "evidence_f1": mean(float(row["evidence_f1"]) for row in rows),
        "citation_precision": mean(float(row["citation_precision"]) for row in rows),
        "citation_recall": mean(float(row["citation_recall"]) for row in rows),
        "answerable_answer_f1": mean(
            float(row["answer_f1"]) for row in answerable_rows
        ),
        "answerable_evidence_f1": mean(
            float(row["evidence_f1"]) for row in answerable_rows
        ),
        "answerable_citation_precision": mean(
            float(row["citation_precision"]) for row in answerable_rows
        ),
        "answerable_citation_recall": mean(
            float(row["citation_recall"]) for row in answerable_rows
        ),
        "answerable_answered": sum(
            row["agent_status"] == "answered" for row in answerable_rows
        ),
        "unanswerable_refused": sum(
            row["agent_status"] == "insufficient_evidence"
            for row in unanswerable_rows
        ),
        "unanswerable_refusal_rate": (
            sum(
                row["agent_status"] == "insufficient_evidence"
                for row in unanswerable_rows
            )
            / len(unanswerable_rows)
            if unanswerable_rows
            else 0.0
        ),
        "generation_errors": sum(
            row["agent_status"] == "generation_error" for row in rows
        ),
        "mean_elapsed_seconds": mean(float(row["elapsed_seconds"]) for row in rows),
    }
    report = {
        "metadata": {
            "purpose": "development_answer_evaluation_not_heldout",
            "source": str(args.source),
            "retrieval_dataset": str(args.retrieval_dataset),
            "split": split_name,
            "model": args.model,
            "retrieval_method": args.retrieval_method.value,
            "reranker_model": (
                args.reranker_model
                if args.retrieval_method
                == SearchMethod.HYBRID_ONTOLOGY_CROSS_ENCODER
                else None
            ),
            "selection": "one question per distinct paper first",
            "concept_links": concept_links,
            "created_at": datetime.now(UTC).isoformat(),
        },
        "summary": summary,
        "cases": rows,
        "limitations": [
            "This is a development sample, not the locked held-out evaluation.",
            "Answer F1 is token overlap and does not replace human correctness review.",
            "Page values are paragraph ordinals because QASPER JSON has no PDF pages.",
        ],
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    output = args.output_dir / f"qasper_answer_evaluation_{stamp}.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2), flush=True)
    print(f"Saved: {output}", flush=True)


if __name__ == "__main__":
    main()
