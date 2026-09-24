import re
import unicodedata
from threading import RLock
from typing import Protocol

import numpy as np
from numpy.typing import NDArray
from rank_bm25 import BM25Okapi

from app.models import Chunk, SearchMethod, SearchResult
from app.ontology.service import OntologyService

_TOKEN = re.compile(r"\w+", re.UNICODE)
DEFAULT_EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


class SemanticModelError(RuntimeError):
    pass


def tokenize(text: str) -> list[str]:
    lowered = text.lower().replace("đ", "d")
    without_accents = "".join(
        character
        for character in unicodedata.normalize("NFD", lowered)
        if unicodedata.category(character) != "Mn"
    )
    return _TOKEN.findall(without_accents)


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
                        method=SearchMethod.BM25,
                        score=max(float(score), 0.0),
                        bm25_score=max(float(score), 0.0),
                        chunk_concepts=chunk.concepts,
                    )
                )
            return results


class TextEncoder(Protocol):
    def encode(self, texts: list[str]) -> NDArray[np.float32]: ...


class SentenceTransformerEncoder:
    """Loads the multilingual embedding model only when semantic search is first used."""

    def __init__(self, model_name: str = DEFAULT_EMBEDDING_MODEL) -> None:
        self.model_name = model_name
        self._model: object | None = None

    def encode(self, texts: list[str]) -> NDArray[np.float32]:
        try:
            if self._model is None:
                from sentence_transformers import SentenceTransformer

                self._model = SentenceTransformer(self.model_name, device="cpu")

            vectors = self._model.encode(  # type: ignore[attr-defined]
                texts,
                batch_size=32,
                show_progress_bar=False,
                convert_to_numpy=True,
                normalize_embeddings=True,
            )
        except Exception as exc:
            raise SemanticModelError(
                f"Could not load or run embedding model '{self.model_name}'"
            ) from exc
        return np.asarray(vectors, dtype=np.float32)


class InMemorySemanticRetriever:
    """Cosine-similarity retrieval using normalized sentence embeddings."""

    def __init__(self, encoder: TextEncoder | None = None) -> None:
        self._chunks: list[Chunk] = []
        self._embeddings: NDArray[np.float32] | None = None
        self._encoder = encoder or SentenceTransformerEncoder()
        self._lock = RLock()

    def add(self, chunks: list[Chunk]) -> None:
        if not chunks:
            return
        with self._lock:
            self._chunks.extend(chunks)
            self._embeddings = None

    def _ensure_index(self) -> None:
        if self._embeddings is None and self._chunks:
            self._embeddings = self._encoder.encode([chunk.text for chunk in self._chunks])

    def search(self, query: str, limit: int = 5) -> list[SearchResult]:
        if not query.strip() or not self._chunks:
            return []

        with self._lock:
            self._ensure_index()
            if self._embeddings is None:
                return []

            query_vector = self._encoder.encode([query])[0]
            scores = self._embeddings @ query_vector
            ranked = np.argsort(scores)[::-1][:limit]

            results: list[SearchResult] = []
            for index in ranked:
                score = min(max(float(scores[index]), 0.0), 1.0)
                results.append(
                    SearchResult(
                        chunk_id=self._chunks[index].id,
                        document_id=self._chunks[index].document_id,
                        filename=self._chunks[index].filename,
                        page=self._chunks[index].page,
                        text=self._chunks[index].text,
                        method=SearchMethod.SEMANTIC,
                        score=score,
                        semantic_score=score,
                        chunk_concepts=self._chunks[index].concepts,
                    )
                )
            return results


class InMemoryHybridRetriever:
    """Combines BM25 and semantic ranks with Reciprocal Rank Fusion (RRF)."""

    def __init__(
        self,
        *,
        semantic_encoder: TextEncoder | None = None,
        ontology_service: OntologyService | None = None,
        rrf_k: int = 60,
        ontology_weight: float = 0.10,
    ) -> None:
        self.bm25 = InMemoryBM25Retriever()
        self.semantic = InMemorySemanticRetriever(semantic_encoder)
        self.ontology = ontology_service
        self.rrf_k = rrf_k
        self.ontology_weight = ontology_weight

    def add(self, chunks: list[Chunk]) -> None:
        self.bm25.add(chunks)
        self.semantic.add(chunks)

    def search(
        self,
        query: str,
        limit: int = 5,
        method: SearchMethod = SearchMethod.HYBRID,
    ) -> list[SearchResult]:
        if method == SearchMethod.BM25:
            return self.bm25.search(query, limit)
        if method == SearchMethod.SEMANTIC:
            return self.semantic.search(query, limit)

        if method == SearchMethod.HYBRID_ONTOLOGY_EXPANSION:
            return self._search_with_ontology(
                query,
                limit,
                method=method,
                use_expansion=True,
                use_reranking=False,
            )
        if method == SearchMethod.HYBRID_ONTOLOGY_RERANK:
            return self._search_with_ontology(
                query,
                limit,
                method=method,
                use_expansion=False,
                use_reranking=True,
            )
        if method == SearchMethod.HYBRID_ONTOLOGY:
            return self._search_with_ontology(
                query,
                limit,
                method=method,
                use_expansion=True,
                use_reranking=True,
            )

        return self._search_hybrid(query, limit)

    def _search_hybrid(self, query: str, limit: int) -> list[SearchResult]:
        candidate_limit = max(limit * 4, 20)
        return self._rank_hybrid_candidates(query, candidate_limit)[:limit]

    def _rank_hybrid_candidates(
        self, query: str, candidate_limit: int
    ) -> list[SearchResult]:
        bm25_results = self.bm25.search(query, candidate_limit)
        semantic_results = self.semantic.search(query, candidate_limit)

        by_id: dict[str, SearchResult] = {}
        fused_scores: dict[str, float] = {}
        bm25_scores = {result.chunk_id: result.score for result in bm25_results}
        semantic_scores = {result.chunk_id: result.score for result in semantic_results}

        for results in (bm25_results, semantic_results):
            for rank, result in enumerate(results, start=1):
                by_id.setdefault(result.chunk_id, result)
                fused_scores[result.chunk_id] = fused_scores.get(result.chunk_id, 0.0) + (
                    1.0 / (self.rrf_k + rank)
                )

        ranked_ids = sorted(fused_scores, key=fused_scores.get, reverse=True)[
            :candidate_limit
        ]
        return [
            by_id[chunk_id].model_copy(
                update={
                    "method": SearchMethod.HYBRID,
                    "score": fused_scores[chunk_id],
                    "bm25_score": bm25_scores.get(chunk_id),
                    "semantic_score": semantic_scores.get(chunk_id),
                }
            )
            for chunk_id in ranked_ids
        ]

    def _search_with_ontology(
        self,
        query: str,
        limit: int,
        *,
        method: SearchMethod,
        use_expansion: bool,
        use_reranking: bool,
    ) -> list[SearchResult]:
        if self.ontology is None:
            return self._search_hybrid(query, limit)

        expansion = self.ontology.expand_query(query)
        retrieval_query = expansion.expanded_query if use_expansion else query
        candidate_limit = max(limit * 4, 20)
        candidates = self._rank_hybrid_candidates(retrieval_query, candidate_limit)
        if not candidates:
            return []

        if not use_reranking:
            return [
                candidate.model_copy(
                    update={
                        "method": method,
                        "query_concepts": expansion.query_concepts,
                        "expanded_query": expansion.expanded_query,
                        "ontology_explanation": "Ontology query expansion only.",
                    }
                )
                for candidate in candidates[:limit]
            ]

        max_rrf = max(candidate.score for candidate in candidates) or 1.0
        reranked: list[SearchResult] = []
        for candidate in candidates:
            match = self.ontology.score_text(query, candidate.text)
            normalized_rrf = candidate.score / max_rrf
            final_score = (
                (1.0 - self.ontology_weight) * normalized_rrf
                + self.ontology_weight * match.score
            )
            reranked.append(
                candidate.model_copy(
                    update={
                        "method": method,
                        "score": final_score,
                        "ontology_score": match.score,
                        "query_concepts": match.query_concepts,
                        "chunk_concepts": match.chunk_concepts,
                        "expanded_query": expansion.expanded_query if use_expansion else None,
                        "ontology_explanation": match.explanation,
                    }
                )
            )

        return sorted(reranked, key=lambda result: result.score, reverse=True)[:limit]
