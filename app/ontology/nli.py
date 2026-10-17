"""Natural-language-inference scoring for ontology concept candidates."""

import numpy as np

DEFAULT_NLI_MODEL = "cross-encoder/nli-deberta-v3-small"
NLI_LABELS = ("contradiction", "entailment", "neutral")


class NliModelError(RuntimeError):
    pass


class SentenceTransformerNliScorer:
    """Return the entailment probability for each premise-hypothesis pair."""

    def __init__(
        self,
        model_name: str = DEFAULT_NLI_MODEL,
        *,
        device: str | None = "cpu",
    ) -> None:
        self.model_name = model_name
        self.device = device
        self._model: object | None = None

    def score_pairs(self, pairs: list[tuple[str, str]]) -> list[float]:
        if not pairs:
            return []
        try:
            if self._model is None:
                from sentence_transformers import CrossEncoder

                self._model = CrossEncoder(self.model_name, device=self.device)
            logits = np.asarray(
                self._model.predict(  # type: ignore[attr-defined]
                    pairs,
                    show_progress_bar=False,
                ),
                dtype=np.float64,
            )
        except Exception as exc:
            raise NliModelError(
                f"Could not load or run NLI model '{self.model_name}'"
            ) from exc
        if logits.ndim != 2 or logits.shape[1] != len(NLI_LABELS):
            raise NliModelError(
                f"NLI model must return three logits in order {NLI_LABELS}"
            )
        shifted = logits - logits.max(axis=1, keepdims=True)
        probabilities = np.exp(shifted)
        probabilities /= probabilities.sum(axis=1, keepdims=True)
        entailment_index = NLI_LABELS.index("entailment")
        return [float(value) for value in probabilities[:, entailment_index]]
