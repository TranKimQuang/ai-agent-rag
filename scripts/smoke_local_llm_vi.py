"""Vietnamese multi-source development smoke, not a held-out evaluation."""

import json
import time
from datetime import UTC, datetime
from pathlib import Path

from app.agent.ollama import GenerationError, OllamaAnswerGenerator
from app.models import SearchMethod, SearchResult


def main():
    evidence = [
        SearchResult(
            chunk_id=f"doc{page}:p{page}:c1",
            document_id=f"doc{page}",
            filename=f"nguon-{page}.txt",
            page=page,
            text=text,
            method=SearchMethod.HYBRID,
            score=1,
        )
        for page, text in enumerate(
            [
                "BM25 tìm kiếm dựa trên từ khóa. Thí nghiệm sử dụng 20 bài báo và 75 câu hỏi.",
                (
                    "Semantic Search so sánh vector embedding để tìm nội dung gần nghĩa. "
                    "Hybrid Search kết hợp thứ hạng từ BM25 và Semantic Search."
                ),
                (
                    "Chỉ mục lưu trong RAM sẽ mất khi server khởi động lại. "
                    "PDF dạng ảnh cần OCR để trích xuất văn bản."
                ),
            ],
            start=1,
        )
    ]
    questions = [
        ("Thí nghiệm dùng bao nhiêu bài báo và câu hỏi?", True),
        ("BM25 và Semantic Search khác nhau thế nào?", True),
        ("Sau khi khởi động lại server cần lưu ý gì và PDF dạng ảnh cần xử lý gì?", True),
        ("Độ chính xác của Hybrid Search trong thí nghiệm là bao nhiêu phần trăm?", False),
    ]
    rows = []
    generator = OllamaAnswerGenerator()
    for question, expected in questions:
        start = time.perf_counter()
        row = {"question": question, "expected_answerable": expected}
        try:
            result = generator.generate(question, evidence)
            answer, citations = result.validated_answer(evidence)
            row.update(
                answer=answer, answered=bool(answer), citations=[c.model_dump() for c in citations]
            )
        except GenerationError as exc:
            row["error"] = str(exc)
        row["seconds"] = round(time.perf_counter() - start, 3)
        rows.append(row)
        print(json.dumps(row, ensure_ascii=True), flush=True)
    path = Path("results") / f"local_llm_vi_{datetime.now(UTC):%Y%m%dT%H%M%SZ}.json"
    path.parent.mkdir(exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "model": generator.model,
                "scope": "synthetic fixed-evidence development only",
                "evidence": [e.model_dump(mode="json") for e in evidence],
                "results": rows,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"Saved {path}")


if __name__ == "__main__":
    main()
