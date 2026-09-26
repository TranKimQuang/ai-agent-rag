"""Run a small end-to-end Agent smoke on QASPER development data.

This script intentionally never uses the held-out split. It checks that real
QASPER text can flow through retrieval, ontology, the evidence gate, the local
LLM and server-owned citations. It is a development diagnostic, not a final
answer-quality benchmark.
"""

import argparse
import json
import time
from datetime import UTC, datetime
from pathlib import Path

from app.agent.ollama import GenerationError, OllamaAnswerGenerator
from app.agent.service import DocumentQuestionAgent
from app.models import Chunk, ConceptLinkingMethod, SearchMethod
from app.ontology.service import OntologyService
from app.rag.retriever import InMemoryHybridRetriever, SentenceTransformerEncoder

DEFAULT_DATASET = Path(
    "evaluation/qasper_train_v3/qasper_train_development.json"
)
DIAGNOSTIC_METHODS = [
    SearchMethod.BM25,
    SearchMethod.SEMANTIC,
    SearchMethod.HYBRID,
    SearchMethod.HYBRID_ONTOLOGY_EXPANSION,
    SearchMethod.HYBRID_ONTOLOGY_RERANK,
    SearchMethod.HYBRID_ONTOLOGY,
]


def select_questions(
    questions: list[dict[str, object]], limit: int
) -> list[dict[str, object]]:
    """Select one question per paper first so a tiny smoke stays diverse."""
    selected: list[dict[str, object]] = []
    seen_papers: set[str] = set()
    for question in questions:
        paper_id = str(question["paper_id"])
        if paper_id in seen_papers:
            continue
        selected.append(question)
        seen_papers.add(paper_id)
        if len(selected) == limit:
            return selected

    selected_ids = {str(question["id"]) for question in selected}
    for question in questions:
        if str(question["id"]) in selected_ids:
            continue
        selected.append(question)
        if len(selected) == limit:
            break
    return selected


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Small end-to-end QASPER development smoke for the local Agent"
    )
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--questions", type=int, default=5)
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--model", default="qwen3:4b")
    parser.add_argument("--output-dir", type=Path, default=Path("results"))
    parser.add_argument(
        "--retrieval-only",
        action="store_true",
        help="Compare retrieval variants without calling Ollama.",
    )
    args = parser.parse_args()
    if args.questions < 1:
        parser.error("--questions must be at least 1")
    if not 1 <= args.limit <= 10:
        parser.error("--limit must be between 1 and 10")

    payload = json.loads(args.dataset.read_text(encoding="utf-8"))
    if "heldout" in str(payload.get("metadata", {}).get("split", "")).lower():
        raise ValueError("This smoke script must not run on the held-out split")

    chunks = [Chunk.model_validate(item) for item in payload["chunks"]]
    questions = select_questions(payload["questions"], args.questions)
    encoder = SentenceTransformerEncoder()
    ontology = OntologyService(
        semantic_encoder=encoder,
        linking_method=ConceptLinkingMethod.HYBRID,
        linking_threshold=0.65,
    )
    chunks, concept_links = ontology.index_chunks(chunks)
    retriever = InMemoryHybridRetriever(
        semantic_encoder=encoder,
        ontology_service=ontology,
    )
    retriever.add(chunks)
    agent = DocumentQuestionAgent(
        retriever,
        answer_generator=OllamaAnswerGenerator(args.model),
    )

    rows: list[dict[str, object]] = []
    for number, item in enumerate(questions, start=1):
        query = str(item["query"])
        gold_ids = {str(value) for value in item["relevant_chunk_ids"]}
        start = time.perf_counter()
        paper_id = str(item["paper_id"])
        by_method = {
            method.value: retriever.search(
                query,
                args.limit,
                method,
                paper_id,
            )
            for method in DIAGNOSTIC_METHODS
        }
        retrieved = by_method[SearchMethod.HYBRID_ONTOLOGY_RERANK.value]
        gold_ranks = {
            method: next(
                (
                    rank
                    for rank, result in enumerate(results, start=1)
                    if result.chunk_id in gold_ids
                ),
                None,
            )
            for method, results in by_method.items()
        }
        if args.retrieval_only:
            response = None
            error = None
        else:
            try:
                response = agent.ask(query, args.limit, paper_id)
                error = None
            except GenerationError as exc:
                response = None
                error = str(exc)
        elapsed = time.perf_counter() - start

        retrieved_ids = [result.chunk_id for result in retrieved]
        gold_rank = next(
            (rank for rank, chunk_id in enumerate(retrieved_ids, start=1) if chunk_id in gold_ids),
            None,
        )
        citation_ids = (
            [citation.chunk_id for citation in response.citations] if response else []
        )
        row = {
            "question_id": item["id"],
            "paper_id": paper_id,
            "query": query,
            "gold_chunk_ids": sorted(gold_ids),
            "retrieved_chunk_ids": retrieved_ids,
            "gold_rank": gold_rank,
            "retrieval_hit": gold_rank is not None,
            "retrieval_gold_ranks": gold_ranks,
            "agent_status": (
                response.status.value
                if response
                else "skipped"
                if args.retrieval_only
                else "generation_error"
            ),
            "answer": response.answer if response else None,
            "citation_chunk_ids": citation_ids,
            "citation_hits_gold": bool(gold_ids.intersection(citation_ids)),
            "confidence": response.confidence if response else None,
            "query_concepts": response.query_concepts if response else [],
            "expanded_query": response.expanded_query if response else None,
            "trace": (
                [step.model_dump(mode="json") for step in response.trace]
                if response
                else []
            ),
            "error": error,
            "elapsed_seconds": round(elapsed, 3),
        }
        rows.append(row)
        print(
            json.dumps(
                {
                    "case": f"{number}/{len(questions)}",
                    "question_id": item["id"],
                    "retrieval_hit": row["retrieval_hit"],
                    "gold_rank": gold_rank,
                    "retrieval_gold_ranks": gold_ranks,
                    "agent_status": row["agent_status"],
                    "citation_hits_gold": row["citation_hits_gold"],
                    "elapsed_seconds": row["elapsed_seconds"],
                },
                ensure_ascii=True,
            ),
            flush=True,
        )

    retrieval_hits = sum(bool(row["retrieval_hit"]) for row in rows)
    answered = sum(row["agent_status"] == "answered" for row in rows)
    citation_hits = sum(bool(row["citation_hits_gold"]) for row in rows)
    retrieval_hits_by_method = {
        method.value: sum(
            row["retrieval_gold_ranks"][method.value] is not None for row in rows
        )
        for method in DIAGNOSTIC_METHODS
    }
    report = {
        "metadata": {
            "purpose": "development_smoke_not_final_benchmark",
            "dataset": str(args.dataset),
            "split": payload.get("metadata", {}).get("split"),
            "selection": "first question from each distinct paper",
            "model": args.model,
            "retrieval_method": SearchMethod.HYBRID_ONTOLOGY_RERANK.value,
            "retrieval_only": args.retrieval_only,
            "questions": len(rows),
            "chunks": len(chunks),
            "concept_links": concept_links,
            "created_at": datetime.now(UTC).isoformat(),
        },
        "summary": {
            "retrieval_hits_at_k": retrieval_hits,
            "retrieval_hits_at_k_by_method": retrieval_hits_by_method,
            "answered": answered,
            "insufficient_evidence": sum(
                row["agent_status"] == "insufficient_evidence" for row in rows
            ),
            "generation_errors": sum(
                row["agent_status"] == "generation_error" for row in rows
            ),
            "answers_with_gold_citation": citation_hits,
            "mean_elapsed_seconds": round(
                sum(float(row["elapsed_seconds"]) for row in rows) / len(rows), 3
            ),
        },
        "cases": rows,
        "limitations": [
            "This is a tiny development smoke, not the locked held-out evaluation.",
            "Gold citation overlap does not by itself prove answer correctness.",
            "QASPER paragraph ordinals are stored in the page field because this JSON has no PDF pages.",
        ],
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    output_path = args.output_dir / f"qasper_agent_smoke_{stamp}.json"
    output_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(report["summary"], ensure_ascii=True), flush=True)
    print(f"Saved: {output_path}", flush=True)


if __name__ == "__main__":
    main()
