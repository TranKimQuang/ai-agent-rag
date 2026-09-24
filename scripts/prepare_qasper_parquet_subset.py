import argparse
import json
from pathlib import Path

from app.evaluation.qasper import build_split, select_qasper_papers


def parquet_row_to_original(row: dict[str, object]) -> tuple[str, dict[str, object]]:
    full_text = row["full_text"]
    qas = row["qas"]
    sections = [
        {"section_name": name, "paragraphs": paragraphs}
        for name, paragraphs in zip(
            full_text["section_name"], full_text["paragraphs"], strict=True
        )
    ]
    questions = []
    for index, question in enumerate(qas["question"]):
        answer_group = qas["answers"][index]
        questions.append(
            {
                "question": question,
                "question_id": qas["question_id"][index],
                "answers": [
                    {"answer": answer} for answer in answer_group["answer"]
                ],
            }
        )
    return str(row["id"]), {
        "title": row["title"],
        "full_text": sections,
        "qas": questions,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create disjoint QASPER development and held-out subsets from Parquet"
    )
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("evaluation/qasper_train"))
    parser.add_argument("--papers", type=int, default=40)
    parser.add_argument("--development-papers", type=int, default=20)
    parser.add_argument("--exclude-dataset", type=Path, action="append", default=[])
    args = parser.parse_args()

    if not 0 < args.development_papers < args.papers:
        raise ValueError("development-papers must be between zero and the paper count")
    try:
        import pyarrow.parquet as pq
    except ImportError as exc:
        raise RuntimeError("Install pyarrow to prepare the Parquet dataset") from exc

    rows = pq.read_table(args.input).to_pylist()
    payload = dict(parquet_row_to_original(row) for row in rows)
    excluded: set[str] = set()
    for path in args.exclude_dataset:
        data = json.loads(path.read_text(encoding="utf-8"))
        excluded.update(data["metadata"]["paper_ids"])

    papers = select_qasper_papers(
        payload,
        paper_limit=args.papers,
        excluded_paper_ids=excluded,
    )
    if len(papers) < args.papers:
        raise ValueError(f"Only {len(papers)} eligible QASPER papers were found")

    outputs = {
        "development": build_split(
            papers[: args.development_papers], split="train_development"
        ),
        "heldout": build_split(
            papers[args.development_papers :], split="train_heldout"
        ),
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name, data in outputs.items():
        path = args.output_dir / f"qasper_train_{name}.json"
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(
            f"{name}: {len(data['metadata']['paper_ids'])} papers, "
            f"{len(data['chunks'])} chunks, {len(data['questions'])} questions -> {path}"
        )


if __name__ == "__main__":
    main()
