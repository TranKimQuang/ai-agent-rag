import argparse
import json
from pathlib import Path

from app.evaluation.benchmark import run_detailed_benchmark
from app.models import SearchMethod
from app.ontology.service import OntologyService
from app.rag.retriever import InMemoryHybridRetriever
from scripts.run_benchmark import load_dataset


def compare_ranks(
    baseline: list[dict[str, object]], candidate: list[dict[str, object]]
) -> dict[str, int]:
    baseline_by_id = {str(row["question_id"]): row["gold_rank"] for row in baseline}
    counts = {"improved": 0, "unchanged": 0, "worsened": 0, "rescued": 0, "lost": 0}
    for row in candidate:
        before = baseline_by_id[str(row["question_id"])]
        after = row["gold_rank"]
        if before is None and isinstance(after, int):
            counts["rescued"] += 1
        elif isinstance(before, int) and after is None:
            counts["lost"] += 1
        elif isinstance(before, int) and isinstance(after, int):
            if after < before:
                counts["improved"] += 1
            elif after > before:
                counts["worsened"] += 1
            else:
                counts["unchanged"] += 1
        else:
            counts["unchanged"] += 1
    return counts


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Tune Ontology re-ranking weight on a validation split"
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        default=Path("evaluation/qasper/qasper_validation.json"),
    )
    parser.add_argument(
        "--weights",
        type=float,
        nargs="+",
        default=[0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.50],
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("evaluation/qasper/ontology_weight_validation_results.json"),
    )
    args = parser.parse_args()

    chunks, questions = load_dataset(args.dataset)
    ontology = OntologyService()
    chunks, concept_links = ontology.index_chunks(chunks)
    retriever = InMemoryHybridRetriever(ontology_service=ontology)
    retriever.add(chunks)

    baseline_summary, baseline_details = run_detailed_benchmark(
        retriever,
        questions,
        methods=[SearchMethod.HYBRID, SearchMethod.HYBRID_ONTOLOGY_EXPANSION],
    )
    baseline_rows = [row for row in baseline_details if row["method"] == "hybrid"]

    by_weight: dict[str, object] = {}
    for weight in sorted(set(args.weights)):
        if not 0.0 <= weight <= 1.0:
            raise ValueError("Ontology weights must be between 0 and 1")
        retriever.ontology_weight = weight
        summary, details = run_detailed_benchmark(
            retriever,
            questions,
            methods=[
                SearchMethod.HYBRID_ONTOLOGY_RERANK,
                SearchMethod.HYBRID_ONTOLOGY,
            ],
        )
        by_weight[f"{weight:.2f}"] = {
            "metrics": summary,
            "rank_changes": {
                method.value: compare_ranks(
                    baseline_rows,
                    [row for row in details if row["method"] == method.value],
                )
                for method in (
                    SearchMethod.HYBRID_ONTOLOGY_RERANK,
                    SearchMethod.HYBRID_ONTOLOGY,
                )
            },
        }

    selected_weight = max(
        by_weight,
        key=lambda weight: (
            by_weight[weight]["metrics"]["hybrid_ontology_rerank"]["ndcg@5"],
            by_weight[weight]["metrics"]["hybrid_ontology_rerank"]["mrr@5"],
            by_weight[weight]["metrics"]["hybrid_ontology_rerank"]["recall@5"],
            -float(weight),
        ),
    )
    payload = {
        "dataset": str(args.dataset),
        "selection_split": "validation",
        "test_split_evaluated": False,
        "questions": len(questions),
        "concept_links": concept_links,
        "selection_metric": "rerank nDCG@5, then MRR@5 and Recall@5",
        "selected_weight": float(selected_weight),
        "baseline": baseline_summary,
        "selected": by_weight[selected_weight],
        "by_weight": by_weight,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
