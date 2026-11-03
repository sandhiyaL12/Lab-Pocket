import json
from unittest.mock import AsyncMock


def _answer():
    return {
        "answer": "Configure a pin with Pin(2, Pin.OUT).",
        "model_used": "test-model",
        "provider": "primary",
        "input_tokens": 2,
        "output_tokens": 3,
        "total_tokens": 5,
        "input_cost_per_million": 1,
        "output_cost_per_million": 2,
        "estimated": False,
    }


def test_chat_returns_small_structured_response_and_records_cost(client, monkeypatch):
    monkeypatch.setattr("app.main.generate_answer", AsyncMock(return_value=_answer()))
    response = client.post(
        "/chat",
        json={"board": "ESP32", "question": "How do I set a pin?"},
    )

    assert response.status_code == 200
    assert len(response.content) < 5000
    assert response.json()["board"] == "ESP32"
    assert response.json()["total_tokens"] == 5

    usage = client.get("/usage").json()
    assert usage == {
        "total_requests": 1,
        "total_input_tokens": 2,
        "total_output_tokens": 3,
        "total_tokens": 5,
        "total_cost_usd": 0.000008,
    }


def test_text_only_chat_returns_plain_text(client, monkeypatch):
    monkeypatch.setattr("app.main.generate_answer", AsyncMock(return_value=_answer()))
    response = client.post(
        "/chat?text_only=true",
        json={"board": "Pico", "question": "How do I set PWM?"},
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    assert response.text == _answer()["answer"]


def test_json_response_supports_gzip(client, monkeypatch):
    monkeypatch.setattr("app.main.generate_answer", AsyncMock(return_value=_answer()))
    response = client.post(
        "/chat",
        headers={"accept-encoding": "gzip"},
        json={"board": "ESP32", "question": "How do I set a pin?"},
    )

    assert response.status_code == 200
    assert response.headers["content-encoding"] == "gzip"
    assert response.json()["answer"] == _answer()["answer"]


def test_chat_truncates_to_under_5_kb(client, monkeypatch):
    oversized = _answer()
    oversized["answer"] = "é" * 8000
    monkeypatch.setattr("app.main.generate_answer", AsyncMock(return_value=oversized))

    response = client.post(
        "/chat",
        json={"board": "ESP32", "question": "How do I set a pin?"},
    )

    assert response.status_code == 200
    assert len(response.content) < 5000
    assert "shortened to fit the 5 KB response limit" in response.json()["answer"]


def test_stream_chat_emits_text_and_done_event(client, monkeypatch):
    async def stream_answer(**_kwargs):
        yield {"type": "delta", "text": "PWM "}
        yield {"type": "delta", "text": "is available."}
        yield {
            "type": "usage",
            "provider": "primary",
            "model_used": "test-model",
            "input_cost_per_million": 0,
            "output_cost_per_million": 0,
            "input_tokens": 1,
            "output_tokens": 2,
            "total_tokens": 3,
            "estimated": False,
        }

    monkeypatch.setattr("app.main.generate_answer_stream", stream_answer)
    response = client.post(
        "/chat/stream",
        json={"board": "RP2", "question": "Does PWM work?"},
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert 'event: token\ndata: "PWM "' in response.text
    assert "event: done" in response.text
    assert (
        json.loads(response.text.split("event: done\ndata: ", 1)[1].split("\n", 1)[0])["board"]
        == "Raspberry Pi Pico"
    )


def test_stream_chat_stays_under_5_kb(client, monkeypatch):
    async def stream_answer(**_kwargs):
        yield {"type": "delta", "text": "é" * 6000}

    monkeypatch.setattr("app.main.generate_answer_stream", stream_answer)
    response = client.post(
        "/chat/stream",
        json={"board": "ESP32", "question": "Give a large answer."},
    )

    assert response.status_code == 200
    assert len(response.content) < 5000
    assert "5 KB stream limit" in response.text


def test_invalid_board_is_rejected(client):
    response = client.post(
        "/chat",
        json={"board": "Arduino", "question": "How do I set a pin?"},
    )
    assert response.status_code == 422
