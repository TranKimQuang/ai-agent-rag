import json

import httpx
import pytest

from app.agent.ollama import GenerationError, LocalAnswer, OllamaAnswerGenerator
from app.models import SearchMethod, SearchResult


def evidence():
    return [
        SearchResult(
            chunk_id="p1",
            document_id="doc",
            filename="a.pdf",
            page=1,
            text="BM25 ranks documents using keywords.",
            method=SearchMethod.HYBRID,
            score=1,
        )
    ]


def output(sentence_id="e1s1"):
    return {
        "answerable": True,
        "claims": [{"text": "BM25 uses keywords.", "sources": [{"sentence_id": sentence_id}]}],
    }


def test_local_generation_uses_structured_local_request():
    def handler(request):
        body = json.loads(request.content)
        assert request.url.host == "127.0.0.1"
        assert body["stream"] is False
        assert body["think"] is False
        assert body["format"]["type"] == "object"
        return httpx.Response(
            200, json={"done": True, "message": {"content": json.dumps(output())}}
        )

    result = OllamaAnswerGenerator(transport=httpx.MockTransport(handler)).generate(
        "What does BM25 use?",
        evidence(),
    )
    text, citations = result.validated_answer(evidence())
    assert text == "BM25 uses keywords. [1]"
    assert citations[0].filename == "a.pdf"
    assert citations[0].quote == evidence()[0].text


@pytest.mark.parametrize(
    "data", [output("fake"), output("e4s1"), {"answerable": False, "claims": []}]
)
def test_invalid_citations_or_refusal_do_not_produce_answer(data):
    assert LocalAnswer.model_validate(data).validated_answer(evidence()) == ("", [])


@pytest.mark.parametrize(
    "body",
    [
        {"done": True, "message": {"content": "not json"}},
        {"done": False},
        {"done": True, "done_reason": "length"},
    ],
)
def test_malformed_or_incomplete_output_is_generation_error(body):
    generator = OllamaAnswerGenerator(
        transport=httpx.MockTransport(lambda request: httpx.Response(200, json=body))
    )
    with pytest.raises(GenerationError):
        generator.generate("Question", evidence())


def test_connection_error_is_not_evidence_refusal():
    def handler(request):
        raise httpx.ConnectError("offline")

    with pytest.raises(GenerationError):
        OllamaAnswerGenerator(transport=httpx.MockTransport(handler)).generate(
            "Question", evidence()
        )


def test_server_resolves_correct_sentence_and_metadata():
    items = evidence()
    items[0].text = "First sentence. The experiment used 20 papers and 75 questions."
    result = LocalAnswer.model_validate(output("e1s2"))
    _, citations = result.validated_answer(items)
    assert citations[0].quote == "The experiment used 20 papers and 75 questions."
    assert citations[0].chunk_id == "p1"


def test_unseen_sentence_is_rejected():
    items = evidence()
    items[0].text = "x" * 1800 + ". Hidden sentence."
    assert LocalAnswer.model_validate(output("e1s2")).validated_answer(items) == ("", [])


def test_bad_id_is_generation_error_not_model_refusal():
    generator = OllamaAnswerGenerator(
        transport=httpx.MockTransport(
            lambda request: httpx.Response(
                200, json={"done": True, "message": {"content": json.dumps(output("fake"))}}
            )
        )
    )
    with pytest.raises(GenerationError):
        generator.generate("Question", evidence())
