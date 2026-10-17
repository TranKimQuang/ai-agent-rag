import numpy as np
import pytest

from app.models import ConceptLink, ConceptLinkingMethod
from app.ontology.nli import NliModelError, SentenceTransformerNliScorer
from app.ontology.service import CrossEncoderConceptCandidate
from scripts.evaluate_nli_concept_linking import predict_nli


class FakeNliModel:
    def predict(
        self, pairs: list[tuple[str, str]], *, show_progress_bar: bool
    ) -> np.ndarray:
        assert show_progress_bar is False
        return np.asarray([[0.0, 2.0, 1.0] for _ in pairs], dtype=np.float32)


def test_nli_scorer_returns_entailment_probabilities() -> None:
    scorer = SentenceTransformerNliScorer()
    scorer._model = FakeNliModel()

    scores = scorer.score_pairs([("premise", "hypothesis")])

    assert scores == pytest.approx([0.66524096])


def test_nli_scorer_rejects_non_nli_output() -> None:
    class BadModel:
        def predict(self, pairs: object, *, show_progress_bar: bool) -> np.ndarray:
            return np.asarray([0.5])

    scorer = SentenceTransformerNliScorer()
    scorer._model = BadModel()

    with pytest.raises(NliModelError, match="three logits"):
        scorer.score_pairs([("premise", "hypothesis")])


def test_predict_nli_keeps_alias_and_supported_candidate() -> None:
    class AliasService:
        query_linking_threshold = 0.55

        def link_concepts(self, *args: object, **kwargs: object) -> list[ConceptLink]:
            return [
                ConceptLink(
                    concept="WordEmbedding",
                    label="word embedding",
                    score=1.0,
                    source=ConceptLinkingMethod.ALIAS,
                )
            ]

    candidates = [
        CrossEncoderConceptCandidate(
            phrase="translated document",
            link=ConceptLink(
                concept="MultilingualNaturalLanguageProcessing",
                label="multilingual natural language processing",
                score=0.42,
                source=ConceptLinkingMethod.SEMANTIC,
            ),
            cross_score=0.82,
        ),
        CrossEncoderConceptCandidate(
            phrase="translated document",
            link=ConceptLink(
                concept="SemanticSearch",
                label="semantic search",
                score=0.41,
                source=ConceptLinkingMethod.SEMANTIC,
            ),
            cross_score=0.30,
        ),
    ]

    prediction = predict_nli(
        AliasService(),  # type: ignore[arg-type]
        "How is a translated document aligned?",
        candidates,
        entailment_threshold=0.70,
        entailment_margin=0.10,
        limit=5,
    )

    assert prediction == {
        "WordEmbedding",
        "MultilingualNaturalLanguageProcessing",
    }
