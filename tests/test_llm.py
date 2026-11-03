import asyncio

import httpx

import app.llm as llm
from app.config import Settings


def test_call_provider_retries_and_sends_authorization(monkeypatch):
    attempts = 0
    real_async_client = httpx.AsyncClient

    def handle(request):
        nonlocal attempts
        attempts += 1
        assert request.headers["Authorization"] == "Bearer test-key"
        if attempts == 1:
            return httpx.Response(503, text="temporary")
        return httpx.Response(
            200,
            json={
                "choices": [{"message": {"content": "Pin works."}}],
                "usage": {"prompt_tokens": 4, "completion_tokens": 3, "total_tokens": 7},
            },
        )

    transport = httpx.MockTransport(handle)

    def make_client(**kwargs):
        return real_async_client(transport=transport, **kwargs)

    monkeypatch.setattr(llm.httpx, "AsyncClient", make_client)
    settings = Settings(
        PRIMARY_API_KEY="test-key",
        LLM_MAX_RETRIES=1,
        LLM_RETRY_DELAY_SECONDS=0,
    )

    result = asyncio.run(
        llm.call_provider(
            settings,
            "test-key",
            "https://provider.test/v1",
            "test-model",
            "ESP32",
            "How does Pin work?",
        )
    )

    assert attempts == 2
    assert result["answer"] == "Pin works."
    assert result["total_tokens"] == 7


def test_generate_answer_uses_fallback_after_primary_failure(monkeypatch):
    calls = []

    async def fake_call_provider(settings, api_key, base_url, model, board, question):
        calls.append(api_key)
        if api_key == "primary-key":
            raise httpx.ConnectError("offline")
        return {
            "answer": "Fallback answer.",
            "model_used": model,
            "input_tokens": 1,
            "output_tokens": 2,
            "total_tokens": 3,
        }

    monkeypatch.setattr(llm, "call_provider", fake_call_provider)
    settings = Settings(
        PRIMARY_API_KEY="primary-key",
        FALLBACK_API_KEY="fallback-key",
        FALLBACK_MODEL="backup-model",
    )

    result = asyncio.run(llm.generate_answer(settings, "ESP32", "Question?"))

    assert calls == ["primary-key", "fallback-key"]
    assert result["provider"] == "fallback"
    assert result["model_used"] == "backup-model"


def test_stream_provider_yields_text_and_usage(monkeypatch):
    real_async_client = httpx.AsyncClient
    stream_body = (
        'data: {"choices":[{"delta":{"content":"first "}}]}\n\n'
        'data: {"choices":[{"delta":{"content":"token"}}]}\n\n'
        'data: {"choices":[],"usage":{"prompt_tokens":2,"completion_tokens":2}}\n\n'
        "data: [DONE]\n\n"
    )
    transport = httpx.MockTransport(
        lambda _request: httpx.Response(
            200,
            headers={"content-type": "text/event-stream"},
            content=stream_body,
        )
    )

    def make_client(**kwargs):
        return real_async_client(transport=transport, **kwargs)

    monkeypatch.setattr(llm.httpx, "AsyncClient", make_client)
    settings = Settings(PRIMARY_API_KEY="test-key", LLM_MAX_RETRIES=0)

    async def collect_events():
        return [
            event
            async for event in llm.stream_provider(
                settings,
                "test-key",
                "https://provider.test/v1",
                "test-model",
                "Pico",
                "Question?",
            )
        ]

    events = asyncio.run(collect_events())

    assert [event["text"] for event in events if event["type"] == "delta"] == [
        "first ",
        "token",
    ]
    assert events[-1]["input_tokens"] == 2
    assert events[-1]["total_tokens"] == 4
