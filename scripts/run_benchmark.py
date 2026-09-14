import argparse
import csv
import json
from pathlib import Path

from app.evaluation.benchmark import BenchmarkQuestion, run_detailed_benchmark
from app.models import Chunk, SearchMethod
from app.ontology.service import OntologyService
from app.rag.retriever import InMemoryHybridRetriever

METHODS = [
    SearchMethod.BM25,
    SearchMethod.SEMANTIC,
    SearchMethod.HYBRID,
    SearchMethod.HYBRID_ONTOLOGY,
]


def load_dataset(path: Path) -> tuple[list[Chunk], list[BenchmarkQuestion]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    chunks = [Chunk.model_validate(item) for item in payload["chunks"]]
    questions = [
        BenchmarkQuestion(
            question_id=item["id"],
            query=item["query"],
            relevant_chunk_ids=set(item["relevant_chunk_ids"]),
            category=item.get("category", "unspecified"),
        )
        for item in payload["questions"]
    ]
    return chunks, questions


def write_csv(report: dict[str, dict[str, float]], path: Path) -> None:
    metric_names = list(next(iter(report.values())))
    with path.open("w", encoding="utf-8-sig", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=["method", *metric_names])
        writer.writeheader()
        for method, metrics in report.items():
            writer.writerow({"method": method, **metrics})


def write_details_csv(details: list[dict[str, object]], path: Path) -> None:
    fields = [
        "question_id",
        "category",
        "query",
        "method",
        "gold_rank",
        "top_chunk_id",
        "gold_chunk_ids",
        "retrieved_chunk_ids",
    ]
    with path.open("w", encoding="utf-8-sig", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()
        for row in details:
            writer.writerow(
                {
                    **row,
                    "gold_chunk_ids": " | ".join(row["gold_chunk_ids"]),
                    "retrieved_chunk_ids": " | ".join(row["retrieved_chunk_ids"]),
                }
            )


def write_ontology_rank_changes(details: list[dict[str, object]], path: Path) -> None:
    by_question_method = {
        (str(row["question_id"]), str(row["method"])): row for row in details
    }
    fields = [
        "question_id",
        "category",
        "query",
        "hybrid_rank",
        "hybrid_ontology_rank",
        "rank_change",
        "outcome",
    ]
    rows = []
    question_ids = sorted({str(row["question_id"]) for row in details})
    for question_id in question_ids:
        hybrid = by_question_method.get((question_id, SearchMethod.HYBRID.value))
        ontology = by_question_method.get(
            (question_id, SearchMethod.HYBRID_ONTOLOGY.value)
        )
        if not hybrid or not ontology:
            continue
        hybrid_rank = hybrid["gold_rank"]
        ontology_rank = ontology["gold_rank"]
        if isinstance(hybrid_rank, int) and isinstance(ontology_rank, int):
            change = hybrid_rank - ontology_rank
            outcome = "improved" if change > 0 else "worsened" if change < 0 else "unchanged"
        else:
            change = None
            outcome = "not_found"
        rows.append(
            {
                "question_id": question_id,
                "category": hybrid["category"],
                "query": hybrid["query"],
                "hybrid_rank": hybrid_rank,
                "hybrid_ontology_rank": ontology_rank,
                "rank_change": change,
                "outcome": outcome,
            }
        )

    with path.open("w", encoding="utf-8-sig", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare four retrieval configurations")
    parser.add_argument(
        "--dataset",
        type=Path,
        default=Path("evaluation/sample_benchmark.json"),
    )
    parser.add_argument("--output-dir", type=Path, default=Path("results"))
    parser.add_argument(
        "--k-values",
        type=int,
        nargs="+",
        default=[1, 3, 5],
        help="Cutoffs used for the summary, for example: --k-values 1 3 5",
    )
    args = parser.parse_args()

    chunks, questions = load_dataset(args.dataset)
    ontology = OntologyService()
    chunks, concept_links = ontology.index_chunks(chunks)
    retriever = InMemoryHybridRetriever(ontology_service=ontology)
    retriever.add(chunks)

    report, details = run_detailed_benchmark(
        retriever,
        questions,
        methods=METHODS,
        k_values=tuple(sorted(set(args.k_values))),
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.output_dir / "retrieval_benchmark.json"
    csv_path = args.output_dir / "retrieval_benchmark.csv"
    details_json_path = args.output_dir / "retrieval_benchmark_details.json"
    details_csv_path = args.output_dir / "retrieval_benchmark_details.csv"
    rank_changes_path = args.output_dir / "ontology_rank_changes.csv"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    write_csv(report, csv_path)
    details_json_path.write_text(
        json.dumps(details, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    write_details_csv(details, details_csv_path)
    write_ontology_rank_changes(details, rank_changes_path)

    print(f"Indexed {len(chunks)} chunks with {concept_links} concept links")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"Saved JSON: {json_path}")
    print(f"Saved CSV: {csv_path}")
    print(f"Saved details: {details_json_path}")
    print(f"Saved details CSV: {details_csv_path}")
    print(f"Saved Ontology rank changes: {rank_changes_path}")


if __name__ == "__main__":
    main()
