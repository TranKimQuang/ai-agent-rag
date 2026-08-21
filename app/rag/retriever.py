import re
from threading import RLock

from rank_bm25 import BM25Okapi

from app.models import Chunk, SearchResult

_TOKEN = re.compile(r"\w+", re.UNICODE)


def tokenize(text: str) -> list[str]:
    return _TOKEN.findall(text.lower())


class InMemoryBM25Retriever:
    """Small development index. Data disappears when the server restarts."""

    def __init__(self) -> None:
        self._chunks: list[Chunk] = []
        self._index: BM25Okapi | None = None
        self._lock = RLock()

    @property
    def chunk_count(self) -> int:
        return len(self._chunks)

    def add(self, chunks: list[Chunk]) -> None:
        if not chunks:
            return
        with self._lock:
            self._chunks.extend(chunks)
            self._index = BM25Okapi([tokenize(chunk.text) for chunk in self._chunks])

    def search(self, query: str, limit: int = 5) -> list[SearchResult]:
        tokens = tokenize(query)
        if not tokens or not self._index:
            return []

        with self._lock:
            scores = self._index.get_scores(tokens)
            ranked = sorted(enumerate(scores), key=lambda item: item[1], reverse=True)

            results: list[SearchResult] = []
            for index, score in ranked:
                if len(results) >= limit:
                    break
                chunk = self._chunks[index]
                if not set(tokens).intersection(tokenize(chunk.text)):
                    continue
                results.append(
                    SearchResult(
                        chunk_id=chunk.id,
                        document_id=chunk.document_id,
                        filename=chunk.filename,
                        page=chunk.page,
                        text=chunk.text,
                        score=max(float(score), 0.0),
                    )
                )
            return results
