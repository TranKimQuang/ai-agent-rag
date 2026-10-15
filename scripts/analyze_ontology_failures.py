import argparse
import json
from pathlib import Path

from app.models import ConceptLinkingMethod
from app.ontology.service import OntologyService, local_name
from app.rag.retriever import SentenceTransformerEncoder
from scripts.run_benchmark import load_dataset


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Describe Ontology coverage without tuning on the evaluated split"
    )
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--details", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--linking-method",
        type=ConceptLinkingMethod,
        choices=list(ConceptLinkingMethod),
        default=ConceptLinkingMethod.HYBRID,
    )
    parser.add_argument("--linking-threshold", type=float, default=0.65)
    parser.add_argument("--query-linking-threshold", type=float)
    parser.add_argument("--query-type-intent", action="store_true")
    parser.add_argument("--query-phrase-linking", action="store_true")
    parser.add_argument("--query-phrase-margin", type=float, default=0.03)
    parser.add_argument(
        "--query-phrase-secondary-threshold-delta", type=float, default=0.05
    )
    parser.add_argument("--document-topic-prior", action="store_true")
    parser.add_argument("--document-topic-bonus", type=float, default=0.05)
    parser.add_argument("--document-topic-penalty", type=float, default=0.05)
    parser.add_argument("--document-topic-chunk-limit", type=int, default=3)
    args = parser.parse_args()

    chunks, questions = load_dataset(args.dataset)
    encoder = (
        SentenceTransformerEncoder()
        if args.linking_method
        in {ConceptLinkingMethod.SEMANTIC, ConceptLinkingMethod.HYBRID}
        else None
    )
    ontology = OntologyService(
        semantic_encoder=encoder,
        linking_method=args.linking_method,
        linking_threshold=args.linking_threshold,
        query_linking_threshold=args.query_linking_threshold,
        query_type_intent=args.query_type_intent,
        query_phrase_linking=args.query_phrase_linking,
        query_phrase_margin=args.query_phrase_margin,
        query_phrase_secondary_threshold_delta=(
            args.query_phrase_secondary_threshold_delta
        ),
        document_topic_prior=args.document_topic_prior,
        document_topic_bonus=args.document_topic_bonus,
        document_topic_penalty=args.document_topic_penalty,
        document_topic_chunk_limit=args.document_topic_chunk_limit,
    )
    chunks, _ = ontology.index_chunks(chunks)
    chunks_by_id = {chunk.id: chunk for chunk in chunks}
    details_payload = json.loads(args.details.read_text(encoding="utf-8"))
    details = (
        details_payload["details"]
        if isinstance(details_payload, dict) and "details" in details_payload
        else details_payload
    )
    ranks = {
        (row["question_id"], row["method"]): row["gold_rank"] for row in details
    }

    rows = []
    for question in questions:
        query_concepts = [
            local_name(concept)
            for concept in ontology.configured_query_concepts(
                question.query, document_id=question.document_id
            )
        ]
        gold_chunks = [
            chunks_by_id[chunk_id]
            for chunk_id in question.relevant_chunk_ids
            if chunk_id in chunks_by_id
        ]
        gold_concepts = sorted(
            {
                concept
                for chunk in gold_chunks
                for concept in chunk.concepts
            }
        )
        best_ontology_score = max(
            (
                ontology.score_concept_names(query_concepts, chunk.concepts).score
                for chunk in gold_chunks
            ),
            default=0.0,
        )
        rows.append(
            {
                "question_id": question.question_id,
                "query": question.query,
                "query_concepts": query_concepts,
                "gold_concepts": gold_concepts,
                "gold_has_ontology_relation": best_ontology_score > 0,
                "hybrid_rank": ranks.get((question.question_id, "hybrid")),
                "ontology_rank": ranks.get(
                    (question.question_id, "hybrid_ontology_rerank")
                ),
            }
        )

    total = len(rows)
    summary = {
        "questions": total,
        "query_with_concept": sum(bool(row["query_concepts"]) for row in rows),
        "gold_evidence_with_concept": sum(bool(row["gold_concepts"]) for row in rows),
        "query_and_gold_with_relation": sum(
            bool(row["gold_has_ontology_relation"]) for row in rows
        ),
        "query_without_concept": sum(not row["query_concepts"] for row in rows),
        "gold_without_concept": sum(not row["gold_concepts"] for row in rows),
    }
    payload = {
        "dataset": str(args.dataset),
        "purpose": "descriptive ontology coverage analysis",
        "linking_method": args.linking_method.value,
        "linking_threshold": args.linking_threshold,
        "query_linking_threshold": (
            args.query_linking_threshold
            if args.query_linking_threshold is not None
            else args.linking_threshold
        ),
        "query_type_intent": args.query_type_intent,
        "query_phrase_linking": args.query_phrase_linking,
        "query_phrase_margin": args.query_phrase_margin,
        "query_phrase_secondary_threshold_delta": (
            args.query_phrase_secondary_threshold_delta
        ),
        "document_topic_prior": args.document_topic_prior,
        "document_topic_bonus": args.document_topic_bonus,
        "document_topic_penalty": args.document_topic_penalty,
        "document_topic_chunk_limit": args.document_topic_chunk_limit,
        "summary": summary,
        "questions": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
