"""Optional second-stage reranking for a small set of retrieval candidates."""

from app.models import SearchResult

DEFAULT_RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L6-v2"


class CrossEncoderModelError(RuntimeError):
    pass


class SentenceTransformerCrossEncoderReranker:
    """Lazily load a cross-encoder and score query-passage pairs."""

    def __init__(
        self,
        model_name: str = DEFAULT_RERANKER_MODEL,
        *,
        device: str | None = "cpu",
    ) -> None:
        self.model_name = model_name
        self.device = device
        self._model: object | None = None

    def score_pairs(self, pairs: list[tuple[str, str]]) -> list[float]:
        """Score arbitrary text pairs without applying retrieval-specific ordering."""
        if not pairs:
            return []
        try:
            if self._model is None:
                from sentence_transformers import CrossEncoder

                self._model = CrossEncoder(self.model_name, device=self.device)
            scores = self._model.predict(  # type: ignore[attr-defined]
                pairs,
                show_progress_bar=False,
            )
        except Exception as exc:
            raise CrossEncoderModelError(
                f"Could not load or run reranker model '{self.model_name}'"
            ) from exc
        return [float(score) for score in scores.tolist()]

    def rerank(
        self, query: str, candidates: list[SearchResult]
    ) -> list[SearchResult]:
        if not candidates:
            return []
        scores = self.score_pairs([(query, candidate.text) for candidate in candidates])
        paired = zip(candidates, scores, strict=True)
        return [
            candidate.model_copy(update={"score": float(score)})
            for candidate, score in sorted(
                paired,
                key=lambda item: item[1],
                reverse=True,
            )
        ]
