"""Controlled answer-generation smoke test, NOT a retrieval/held-out benchmark."""

import json
import time
from datetime import UTC, datetime
from pathlib import Path

from app.agent.ollama import GenerationError, OllamaAnswerGenerator
from app.models import SearchMethod, SearchResult


def main():
    generator = OllamaAnswerGenerator()
    evidence = [
        SearchResult(
            chunk_id="smoke:p1:c1",
            document_id="smoke",
            filename="controlled-fixture.txt",
            page=1,
            method=SearchMethod.HYBRID,
            score=1,
            text=(
                "BM25 ranks documents using keyword matches. Semantic search compares "
                "embedding vectors. Hybrid search combines keyword and semantic rankings. "
                "The experiment used 20 papers and 75 questions. Results are stored in RAM "
                "and disappear when the server restarts. Scanned PDFs require OCR."
            ),
        )
    ]
    questions = [
        ("What does BM25 use?", True),
        ("How does semantic search compare documents?", True),
        ("What does hybrid search combine?", True),
        ("How many papers were used?", True),
        ("How many questions were used?", True),
        ("What happens to stored results after restart?", True),
        ("What do scanned PDFs require?", True),
        ("What accuracy did the experiment achieve?", False),
        ("Who authored the papers?", False),
        ("What is today's gold price?", False),
    ]
    rows = []
    for question, expected in questions:
        start = time.perf_counter()
        try:
            result = generator.generate(question, evidence)
            answer, citations = result.validated_answer(evidence)
            rows.append(
                {
                    "question": question,
                    "expected_answerable": expected,
                    "answered": bool(answer),
                    "answer": answer,
                    "citations": [c.model_dump() for c in citations],
                    "seconds": round(time.perf_counter() - start, 3),
                    "human_correctness": None,
                    "human_citation_support": None,
                }
            )
            print(
                f"Case {len(rows)}/{len(questions)}: answered={bool(answer)}, "
                f"expected={expected}, seconds={rows[-1]['seconds']}",
                flush=True,
            )
        except GenerationError as exc:
            rows.append({"question": question, "error": str(exc)})
            break
    path = Path("results") / (
        "local_llm_sentence_ids_" + datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ") + ".json"
    )
    path.parent.mkdir(exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "model": generator.model,
                "scope": "synthetic fixed-evidence smoke; not QASPER evaluation",
                "results": rows,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"Saved {len(rows)} attempted cases to {path}")
    if any("error" in row for row in rows):
        raise SystemExit("Ollama/model unavailable; real-model evaluation incomplete.")


if __name__ == "__main__":
    main()
