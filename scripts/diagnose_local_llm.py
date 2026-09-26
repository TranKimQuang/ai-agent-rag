"""Inspect count questions using the current adapter; preserve raw local outputs."""

import json
import time
from datetime import UTC, datetime
from pathlib import Path

import httpx

from app.agent.ollama import GenerationError, LocalAnswer, OllamaAnswerGenerator, sentence_sources
from app.models import SearchMethod, SearchResult


class RecordingTransport(httpx.BaseTransport):
    def __init__(self):
        self.inner = httpx.HTTPTransport()
        self.response_body = None
        self.request_body = None

    def handle_request(self, request):
        self.request_body = json.loads(request.content)
        response = self.inner.handle_request(request)
        response.read()
        self.response_body = response.json()
        return response

    def close(self):
        self.inner.close()


def main():
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
    rows = []
    for question in ["How many papers were used?", "How many questions were used?"]:
        transport = RecordingTransport()
        start = time.perf_counter()
        row = {"question": question}
        try:
            result = OllamaAnswerGenerator(transport=transport).generate(question, evidence)
            row["pipeline_output"] = result.model_dump()
            raw = LocalAnswer.model_validate_json(transport.response_body["message"]["content"])
            reasons = []
            if not raw.answerable:
                reasons.append("model_refusal")
            elif not raw.claims:
                reasons.append("empty_claims")
            for claim in raw.claims:
                if not claim.text.strip():
                    reasons.append("blank_claim")
                for source in claim.sources:
                    if source.sentence_id not in sentence_sources(evidence):
                        reasons.append("unknown_sentence_id")
            row["reasons"] = reasons or ["accepted"]
        except (GenerationError, ValueError, KeyError, TypeError) as exc:
            row["error"] = str(exc)
        row["seconds"] = round(time.perf_counter() - start, 3)
        row["request"] = transport.request_body
        row["raw_response"] = transport.response_body
        rows.append(row)
        print(json.dumps(row, ensure_ascii=False), flush=True)
    path = Path("results") / (
        "local_llm_diagnostic_" + datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ") + ".json"
    )
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved {path}")


if __name__ == "__main__":
    main()
