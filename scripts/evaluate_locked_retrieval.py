import argparse
import json
from pathlib import Path

from app.evaluation.benchmark import run_detailed_benchmark
from app.models import ConceptLinkingMethod, SearchMethod
from app.ontology.service import OntologyService
from app.rag.retriever import InMemoryHybridRetriever, SentenceTransformerEncoder
from scripts.run_benchmark import load_dataset
from scripts.tune_ontology_weight import compare_ranks

ONTOLOGY_METHODS = [
    SearchMethod.HYBRID_ONTOLOGY_EXPANSION,
    SearchMethod.HYBRID_ONTOLOGY_RERANK,
    SearchMethod.HYBRID_ONTOLOGY,
]
EVALUATION_METHODS = [
    SearchMethod.BM25,
    SearchMethod.SEMANTIC,
    SearchMethod.HYBRID,
    *ONTOLOGY_METHODS,
]


def summarize_rank_changes(
    details: list[dict[str, object]],
) -> dict[str, dict[str, int]]:
    baseline = [row for row in details if row["method"] == SearchMethod.HYBRID.value]
    return {
        method.value: compare_ranks(
            baseline,
            [row for row in details if row["method"] == method.value],
        )
        for method in ONTOLOGY_METHODS
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Evaluate a frozen retrieval configuration without tuning"
    )
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    config = json.loads(args.config.read_text(encoding="utf-8"))
    if config.get("configuration_status") != "frozen_before_evaluation":
        raise ValueError("Configuration must be frozen before evaluation")
    if config.get("evaluation_status") != "not_evaluated":
        raise ValueError("Locked dataset has already been evaluated")

    chunks, questions = load_dataset(args.dataset)
    encoder = SentenceTransformerEncoder()
    ontology = OntologyService(
        semantic_encoder=encoder,
        linking_method=ConceptLinkingMethod(config["concept_linking_method"]),
        linking_threshold=float(config["concept_linking_threshold"]),
        query_type_intent=bool(config["query_type_intent"]),
    )
    chunks, concept_links = ontology.index_chunks(chunks)
    retriever = InMemoryHybridRetriever(
        semantic_encoder=encoder,
        ontology_service=ontology,
        ontology_weight=float(config["ontology_weight"]),
    )
    retriever.add(chunks)

    k_values = tuple(sorted({int(value) for value in config["k_values"]}))
    summary, details = run_detailed_benchmark(
        retriever,
        questions,
        methods=EVALUATION_METHODS,
        k_values=k_values,
    )
    payload = {
        "protocol": "locked_retrieval_evaluation",
        "dataset": str(args.dataset),
        "config": str(args.config),
        "configuration": config,
        "chunks": len(chunks),
        "questions": len(questions),
        "concept_links": concept_links,
        "summary": summary,
        "rank_changes_from_hybrid": summarize_rank_changes(details),
        "details": details,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps({key: value for key, value in payload.items() if key != "details"}, indent=2))
    print(f"Saved locked evaluation: {args.output}")


if __name__ == "__main__":
    main()
