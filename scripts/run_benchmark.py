import argparse
import csv
import json
from pathlib import Path

from app.evaluation.benchmark import BenchmarkQuestion, run_benchmark
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


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare four retrieval configurations")
    parser.add_argument(
        "--dataset",
        type=Path,
        default=Path("evaluation/sample_benchmark.json"),
    )
    parser.add_argument("--output-dir", type=Path, default=Path("results"))
    parser.add_argument("--k", type=int, default=5)
    args = parser.parse_args()

    chunks, questions = load_dataset(args.dataset)
    ontology = OntologyService()
    chunks, concept_links = ontology.index_chunks(chunks)
    retriever = InMemoryHybridRetriever(ontology_service=ontology)
    retriever.add(chunks)

    report = run_benchmark(retriever, questions, methods=METHODS, k=args.k)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.output_dir / "retrieval_benchmark.json"
    csv_path = args.output_dir / "retrieval_benchmark.csv"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    write_csv(report, csv_path)

    print(f"Indexed {len(chunks)} chunks with {concept_links} concept links")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"Saved JSON: {json_path}")
    print(f"Saved CSV: {csv_path}")


if __name__ == "__main__":
    main()
