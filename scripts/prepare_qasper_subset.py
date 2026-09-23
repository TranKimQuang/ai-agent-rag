import argparse
import json
from pathlib import Path

from app.evaluation.qasper import build_split, select_qasper_papers


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a deterministic QASPER retrieval subset")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("evaluation/qasper"))
    parser.add_argument("--papers", type=int, default=20)
    parser.add_argument("--validation-papers", type=int, default=10)
    parser.add_argument("--min-questions-per-paper", type=int, default=3)
    parser.add_argument("--max-questions-per-paper", type=int, default=5)
    args = parser.parse_args()

    if not 0 < args.validation_papers < args.papers:
        raise ValueError("validation-papers must be between zero and the paper count")

    payload = json.loads(args.input.read_text(encoding="utf-8"))
    papers = select_qasper_papers(
        payload,
        paper_limit=args.papers,
        min_questions_per_paper=args.min_questions_per_paper,
        max_questions_per_paper=args.max_questions_per_paper,
    )
    if len(papers) < args.papers:
        raise ValueError(f"Only {len(papers)} eligible QASPER papers were found")

    validation = build_split(papers[: args.validation_papers], split="validation")
    test = build_split(papers[args.validation_papers :], split="test")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "validation": (args.output_dir / "qasper_validation.json", validation),
        "test": (args.output_dir / "qasper_test.json", test),
    }
    for name, (path, data) in outputs.items():
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(
            f"{name}: {len(data['metadata']['paper_ids'])} papers, "
            f"{len(data['chunks'])} chunks, {len(data['questions'])} questions -> {path}"
        )


if __name__ == "__main__":
    main()
