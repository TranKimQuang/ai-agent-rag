import argparse
import csv
import json
from pathlib import Path

from rdflib import RDF
from rdflib.namespace import SKOS

from app.models import Chunk, ConceptLinkingMethod
from app.ontology.service import QA, OntologyService, local_name
from app.rag.retriever import SentenceTransformerEncoder
from scripts.run_benchmark import load_dataset


def collect_result_rows(
    ontology: OntologyService, chunks: list[Chunk]
) -> list[dict[str, object]]:
    chunks_by_resource = {
        QA[f"chunk-{chunk.id}"]: chunk
        for chunk in chunks
    }
    predicates = {
        "methods": QA.resultUsesMethod,
        "models": QA.resultUsesModel,
        "datasets": QA.resultUsesDataset,
        "metrics": QA.measuredBy,
    }
    rows: list[dict[str, object]] = []
    results = sorted(
        (
            value
            for value in ontology.graph.subjects(RDF.type, QA.Result)
            if value != QA.SampleResult
        ),
        key=str,
    )
    for result in results:
        chunk_resource = next(ontology.graph.objects(result, QA.hasEvidence), None)
        chunk = chunks_by_resource.get(chunk_resource)
        if chunk is None:
            continue
        row: dict[str, object] = {
            "result_id": local_name(result),
            "document_id": chunk.document_id,
            "chunk_id": chunk.id,
            "page": chunk.page,
            "text": chunk.text,
        }
        for field, predicate in predicates.items():
            labels = []
            for value in ontology.graph.objects(result, predicate):
                label = ontology.graph.value(value, SKOS.prefLabel)
                labels.append(str(label) if label is not None else local_name(value))
            row[field] = " | ".join(sorted(set(labels), key=str.lower))
        row["values"] = " | ".join(
            sorted({str(value) for value in ontology.graph.objects(result, QA.metricValue)})
        )
        row["review_status"] = "pending"
        row["review_note"] = ""
        rows.append(row)
    return rows


def _split_links(value: object) -> list[str]:
    return [item for item in str(value).split(" | ") if item]


def apply_review_annotations(
    rows: list[dict[str, object]], review: dict[str, object]
) -> list[dict[str, object]]:
    """Merge a reproducible manual review into exported Result rows."""
    annotations = review.get("annotations", {})
    if not isinstance(annotations, dict):
        raise TypeError("Review annotations must be a JSON object")

    role_fields = ("methods", "models", "datasets", "metrics", "values")
    for row in rows:
        result_id = str(row["result_id"])
        annotation = annotations.get(result_id, {})
        if not isinstance(annotation, dict):
            raise TypeError(f"Review annotation for {result_id} must be an object")

        result_status = str(annotation.get("result_status", "in_scope"))
        row["result_review"] = result_status
        role_has_issue = False
        for field in role_fields:
            links = _split_links(row[field])
            invalid = [str(value) for value in annotation.get(f"{field}_invalid", [])]
            ambiguous = [
                str(value) for value in annotation.get(f"{field}_ambiguous", [])
            ]
            unknown = (set(invalid) | set(ambiguous)) - set(links)
            if unknown:
                raise ValueError(
                    f"Review for {result_id}/{field} references missing links: "
                    f"{sorted(unknown)}"
                )
            if not links:
                status = "not_present"
            elif ambiguous:
                status = "ambiguous" if len(ambiguous) == len(links) else "mixed"
            elif invalid:
                status = "incorrect" if len(invalid) == len(links) else "mixed"
            else:
                status = "correct"
            row[f"{field}_review"] = status
            row[f"{field}_invalid"] = " | ".join(invalid)
            row[f"{field}_ambiguous"] = " | ".join(ambiguous)
            role_has_issue = role_has_issue or status in {
                "incorrect",
                "mixed",
                "ambiguous",
            }

        if result_status in {"non_result", "prior_work"}:
            row["review_status"] = "rejected"
        elif result_status == "ambiguous":
            row["review_status"] = "ambiguous"
        elif role_has_issue:
            row["review_status"] = "needs_fix"
        else:
            row["review_status"] = "accepted"
        row["review_note"] = str(annotation.get("note", ""))
    return rows


def summarize_review(rows: list[dict[str, object]]) -> dict[str, object]:
    role_fields = ("methods", "models", "datasets", "metrics", "values")
    result_counts: dict[str, int] = {}
    for row in rows:
        status = str(row["result_review"])
        result_counts[status] = result_counts.get(status, 0) + 1

    role_precision: dict[str, dict[str, int | float | None]] = {}
    for field in role_fields:
        total = correct = incorrect = ambiguous = 0
        for row in rows:
            links = _split_links(row[field])
            invalid = set(_split_links(row[f"{field}_invalid"]))
            unclear = set(_split_links(row[f"{field}_ambiguous"]))
            total += len(links)
            incorrect += len(invalid)
            ambiguous += len(unclear)
            correct += len(links) - len(invalid) - len(unclear)
        denominator = correct + incorrect
        role_precision[field] = {
            "total_links": total,
            "correct": correct,
            "incorrect": incorrect,
            "ambiguous": ambiguous,
            "reviewed_precision": round(correct / denominator, 4)
            if denominator
            else None,
        }

    result_denominator = len(rows) - result_counts.get("ambiguous", 0)
    return {
        "rows": len(rows),
        "result_counts": result_counts,
        "result_instance_precision": round(
            result_counts.get("in_scope", 0) / result_denominator, 4
        )
        if result_denominator
        else None,
        "role_precision": role_precision,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export paper-scoped Result facts for manual precision review"
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        default=Path("evaluation/qasper_protocol_v4/qasper_development.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("evaluation/qasper_protocol_v4/result_context_audit.csv"),
    )
    parser.add_argument(
        "--review",
        type=Path,
        default=Path("evaluation/qasper_protocol_v4/result_context_review.json"),
    )
    parser.add_argument(
        "--summary",
        type=Path,
        default=Path("evaluation/qasper_protocol_v4/result_context_audit_summary.json"),
    )
    args = parser.parse_args()

    chunks, _ = load_dataset(args.dataset)
    encoder = SentenceTransformerEncoder()
    ontology = OntologyService(
        semantic_encoder=encoder,
        linking_method=ConceptLinkingMethod.HYBRID,
        linking_threshold=0.65,
    )
    indexed_chunks, _ = ontology.index_chunks(chunks)
    rows = collect_result_rows(ontology, indexed_chunks)
    if args.review.exists():
        review = json.loads(args.review.read_text(encoding="utf-8"))
        rows = apply_review_annotations(rows, review)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "result_id",
        "document_id",
        "chunk_id",
        "page",
        "methods",
        "models",
        "datasets",
        "metrics",
        "values",
        "text",
        "result_review",
        "methods_review",
        "models_review",
        "datasets_review",
        "metrics_review",
        "values_review",
        "methods_invalid",
        "models_invalid",
        "datasets_invalid",
        "metrics_invalid",
        "values_invalid",
        "methods_ambiguous",
        "models_ambiguous",
        "datasets_ambiguous",
        "metrics_ambiguous",
        "values_ambiguous",
        "review_status",
        "review_note",
    ]
    with args.output.open("w", encoding="utf-8-sig", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    if args.review.exists():
        args.summary.write_text(
            json.dumps(summarize_review(rows), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    print(f"Exported {len(rows)} Result rows to {args.output}")


if __name__ == "__main__":
    main()
