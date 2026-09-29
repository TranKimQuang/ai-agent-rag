import json

import httpx
import pytest

from app.agent.ollama import (
    GenerationError,
    LocalAnswer,
    OllamaAnswerGenerator,
    OllamaAnswerSupportVerifier,
    infer_answer_format,
)
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
        system_prompt = body["messages"][0]["content"]
        assert "Start with the direct answer" in system_prompt
        assert "begin exactly Yes or No" in system_prompt
        assert "Prefer one concise claim" in system_prompt
        user_payload = json.loads(body["messages"][1]["content"])
        assert user_payload["answer_format"] == "short_phrase_or_list"
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
    ("question", "expected"),
    [
        ("Do they evaluate on QASPER?", "boolean"),
        ("How many papers are evaluated?", "number"),
        ("By how much does accuracy improve?", "number"),
        ("What models are tested?", "short_phrase_or_list"),
        ("How are bidirectional LMs obtained?", "explanation"),
    ],
)
def test_infer_answer_format(question, expected) -> None:
    assert infer_answer_format(question) == expected


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


def test_sentence_ids_can_reference_a_fifth_exposed_chunk():
    items = [
        evidence()[0].model_copy(
            update={"chunk_id": f"p{number}", "page": number, "text": f"Evidence {number}."}
        )
        for number in range(1, 6)
    ]
    result = LocalAnswer.model_validate(output("e5s1"))

    _, citations = result.validated_answer(items)

    assert citations[0].chunk_id == "p5"


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


def test_transient_invalid_output_is_retried_once():
    attempts = 0

    def handler(request):
        nonlocal attempts
        attempts += 1
        content = "not json" if attempts == 1 else json.dumps(output())
        return httpx.Response(200, json={"done": True, "message": {"content": content}})

    result = OllamaAnswerGenerator(
        transport=httpx.MockTransport(handler),
        max_attempts=2,
    ).generate("What does BM25 use?", evidence())

    assert attempts == 2
    assert result.answerable is True


def test_support_verifier_uses_exact_question_answer_and_quotes():
    def handler(request):
        body = json.loads(request.content)
        user_payload = json.loads(body["messages"][1]["content"])
        assert user_payload["question"] == "What does BM25 use?"
        assert user_payload["proposed_answer"] == "BM25 uses keywords."
        assert user_payload["cited_evidence"][0]["quote"] == evidence()[0].text
        return httpx.Response(
            200,
            json={
                "done": True,
                "message": {
                    "content": json.dumps(
                        {
                            "supported": True,
                            "confidence": 0.95,
                            "reason": "The citation directly states the answer.",
                        }
                    )
                },
            },
        )

    citation = LocalAnswer.model_validate(output()).validated_answer(evidence())[1][0]
    verdict = OllamaAnswerSupportVerifier(
        transport=httpx.MockTransport(handler)
    ).verify("What does BM25 use?", "BM25 uses keywords. [1]", [citation])

    assert verdict.supported is True
    assert verdict.confidence == 0.95


def test_support_verifier_rejects_answer_without_citation_without_calling_model():
    def handler(request):
        raise AssertionError("Verifier must not run without citations")

    verdict = OllamaAnswerSupportVerifier(
        transport=httpx.MockTransport(handler)
    ).verify("Question", "Answer", [])

    assert verdict.supported is False
    assert verdict.confidence == 1.0
