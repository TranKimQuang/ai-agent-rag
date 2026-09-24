import argparse
import json
from pathlib import Path

from app.ontology.service import OntologyService, local_name
from scripts.run_benchmark import load_dataset


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Describe Ontology coverage without tuning on the evaluated split"
    )
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--details", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    chunks, questions = load_dataset(args.dataset)
    chunks_by_id = {chunk.id: chunk for chunk in chunks}
    ontology = OntologyService()
    details = json.loads(args.details.read_text(encoding="utf-8"))
    ranks = {
        (row["question_id"], row["method"]): row["gold_rank"] for row in details
    }

    rows = []
    for question in questions:
        query_concepts = [
            local_name(concept) for concept in ontology.identify_concepts(question.query)
        ]
        gold_texts = [
            chunks_by_id[chunk_id].text
            for chunk_id in question.relevant_chunk_ids
            if chunk_id in chunks_by_id
        ]
        gold_concepts = sorted(
            {
                local_name(concept)
                for text in gold_texts
                for concept in ontology.identify_concepts(text)
            }
        )
        best_ontology_score = max(
            (ontology.score_text(question.query, text).score for text in gold_texts),
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
        "summary": summary,
        "questions": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
