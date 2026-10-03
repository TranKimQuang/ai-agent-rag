from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.evaluation.ontology_quality import evaluate_ontology, render_markdown
from app.ontology.service import DEFAULT_ONTOLOGY_PATH


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run OWL-RL consistency and competency-question evaluation."
    )
    parser.add_argument("--ontology", type=Path, default=DEFAULT_ONTOLOGY_PATH)
    parser.add_argument(
        "--queries",
        type=Path,
        default=Path(__file__).parents[1] / "ontology" / "queries",
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("evaluation/ontology_quality_report.json"),
    )
    parser.add_argument(
        "--markdown-output",
        type=Path,
        default=Path("evaluation/ONTOLOGY_QUALITY_REPORT.md"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = evaluate_ontology(args.ontology, args.queries)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    args.markdown_output.write_text(render_markdown(report), encoding="utf-8")
    print(
        f"consistent={report['consistent']} "
        f"competency_questions="
        f"{report['competency_questions_passed']}/"
        f"{report['competency_questions_total']}"
    )
    print(args.json_output)
    print(args.markdown_output)


if __name__ == "__main__":
    main()
