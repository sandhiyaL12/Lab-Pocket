import asyncio
import json
import logging
from collections.abc import AsyncIterator
from typing import Any

import httpx

from app.config import Settings

logger = logging.getLogger(__name__)


def _providers(
    settings: Settings,
) -> list[tuple[str, str | None, str, str, float, float]]:
    return [
        (
            "primary",
            settings.primary_api_key,
            settings.primary_base_url,
            settings.primary_model,
            settings.primary_input_cost_per_million,
            settings.primary_output_cost_per_million,
        ),
        (
            "fallback",
            settings.fallback_api_key,
            settings.fallback_base_url,
            settings.fallback_model,
            settings.fallback_input_cost_per_million,
            settings.fallback_output_cost_per_million,
        ),
    ]


def _request_data(
    settings: Settings,
    model: str,
    board: str,
    question: str,
    *,
    stream: bool = False,
) -> dict[str, Any]:
    return {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are Lab-Pocket, a MicroPython assistant for ECE students. "
                    "Give a concise, accurate, practical answer for the selected board. "
                    "Do not claim source verification unless source excerpts are provided."
                ),
            },
            {
                "role": "user",
                "content": f"Board: {board}\nQuestion: {question}",
            },
        ],
        "max_tokens": settings.max_output_tokens,
        "stream": stream,
    }


def _message_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(
            item["text"] for item in content if isinstance(item, dict) and isinstance(item.get("text"), str)
        )
    return ""


def _token_count(value: Any) -> int:
    return value if isinstance(value, int) and not isinstance(value, bool) and value >= 0 else 0


def _retryable(error: Exception) -> bool:
    if isinstance(error, httpx.HTTPStatusError):
        return error.response.status_code == 429 or error.response.status_code >= 500
    return isinstance(error, httpx.TransportError)


async def _retry_pause(settings: Settings, attempt: int) -> None:
    if settings.retry_delay_seconds:
        await asyncio.sleep(settings.retry_delay_seconds * (attempt + 1))


async def call_provider(
    settings: Settings,
    api_key: str,
    base_url: str,
    model: str,
    board: str,
    question: str,
) -> dict[str, Any]:
    url = f"{base_url.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = _request_data(settings, model, board, question)

    for attempt in range(settings.max_retries + 1):
        try:
            async with httpx.AsyncClient(timeout=settings.timeout_seconds) as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()

            choices = data.get("choices", [])
            if not choices or not isinstance(choices[0], dict):
                raise ValueError("API response does not contain a valid choice.")
            message = choices[0].get("message", {})
            answer = _message_text(message.get("content")) if isinstance(message, dict) else ""
            if not answer.strip():
                raise ValueError("API returned an empty answer.")

            usage = data.get("usage")
            if not isinstance(usage, dict):
                usage = {}
            input_tokens = _token_count(usage.get("prompt_tokens"))
            output_tokens = _token_count(usage.get("completion_tokens"))
            total_tokens = _token_count(usage.get("total_tokens"))
            return {
                "answer": answer.strip(),
                "model_used": model,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": total_tokens or input_tokens + output_tokens,
                "estimated": not bool(input_tokens or output_tokens),
            }
        except (httpx.HTTPError, ValueError) as error:
            if attempt >= settings.max_retries or not _retryable(error):
                raise
            logger.warning("Transient LLM request failure; retrying (attempt %s).", attempt + 1)
            await _retry_pause(settings, attempt)

    raise RuntimeError("LLM request retries exhausted.")


async def _stream_provider_once(
    settings: Settings,
    api_key: str,
    base_url: str,
    model: str,
    board: str,
    question: str,
) -> AsyncIterator[dict[str, Any]]:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = _request_data(settings, model, board, question, stream=True)
    input_tokens = output_tokens = 0
    received_text = False

    async with httpx.AsyncClient(timeout=settings.timeout_seconds) as client:
        async with client.stream(
            "POST",
            f"{base_url.rstrip('/')}/chat/completions",
            headers=headers,
            json=payload,
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line.startswith("data:"):
                    continue
                chunk_text = line[5:].strip()
                if chunk_text == "[DONE]":
                    break
                chunk = json.loads(chunk_text)
                usage = chunk.get("usage")
                if isinstance(usage, dict):
                    input_tokens = _token_count(usage.get("prompt_tokens")) or input_tokens
                    output_tokens = _token_count(usage.get("completion_tokens")) or output_tokens
                choices = chunk.get("choices", [])
                if not choices or not isinstance(choices[0], dict):
                    continue
                delta = choices[0].get("delta", {})
                text = _message_text(delta.get("content")) if isinstance(delta, dict) else ""
                if text:
                    received_text = True
                    yield {"type": "delta", "text": text}

    if not received_text:
        raise ValueError("API returned an empty streamed answer.")
    yield {
        "type": "usage",
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "estimated": not bool(input_tokens or output_tokens),
    }


async def stream_provider(
    settings: Settings,
    api_key: str,
    base_url: str,
    model: str,
    board: str,
    question: str,
) -> AsyncIterator[dict[str, Any]]:
    for attempt in range(settings.max_retries + 1):
        received_text = False
        try:
            async for event in _stream_provider_once(settings, api_key, base_url, model, board, question):
                if event["type"] == "delta":
                    received_text = True
                yield event
            return
        except (httpx.HTTPError, ValueError) as error:
            if received_text or attempt >= settings.max_retries or not _retryable(error):
                raise
            logger.warning("Transient streamed LLM failure; retrying (attempt %s).", attempt + 1)
            await _retry_pause(settings, attempt)


def _provider_error(name: str, error: Exception) -> str:
    if isinstance(error, httpx.HTTPStatusError):
        return f"{name} HTTP {error.response.status_code}"
    if isinstance(error, httpx.HTTPError):
        return f"{name} network error"
    return f"{name} returned an invalid response"


async def generate_answer(settings: Settings, board: str, question: str) -> dict[str, Any]:
    errors = []
    attempted = 0
    for name, api_key, base_url, model, input_price, output_price in _providers(settings):
        if not api_key or not model:
            continue
        attempted += 1
        try:
            result = await call_provider(settings, api_key, base_url, model, board, question)
            result.update(
                provider=name,
                input_cost_per_million=input_price,
                output_cost_per_million=output_price,
            )
            return result
        except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError) as error:
            logger.warning("%s LLM provider failed: %s", name, _provider_error(name, error))
            errors.append(_provider_error(name, error))

    if not attempted:
        raise RuntimeError("No LLM provider is configured. Set a provider API key and model.")
    raise RuntimeError("All configured LLM providers failed: " + "; ".join(errors))


async def generate_answer_stream(
    settings: Settings,
    board: str,
    question: str,
) -> AsyncIterator[dict[str, Any]]:
    errors = []
    attempted = 0
    for name, api_key, base_url, model, input_price, output_price in _providers(settings):
        if not api_key or not model:
            continue
        attempted += 1
        received_text = False
        try:
            async for event in stream_provider(settings, api_key, base_url, model, board, question):
                if event["type"] == "delta":
                    received_text = True
                event.update(
                    provider=name,
                    model_used=model,
                    input_cost_per_million=input_price,
                    output_cost_per_million=output_price,
                )
                yield event
            return
        except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError) as error:
            logger.warning("%s streamed LLM provider failed: %s", name, _provider_error(name, error))
            if received_text:
                raise RuntimeError("LLM stream interrupted after answer text began.") from error
            errors.append(_provider_error(name, error))

    if not attempted:
        raise RuntimeError("No LLM provider is configured. Set a provider API key and model.")
    raise RuntimeError("All configured LLM providers failed: " + "; ".join(errors))
