
import httpx

from app.config import Settings


async def call_provider(
    settings: Settings,
    api_key: str,
    base_url: str,
    model: str,
    board: str,
    question: str,
) -> dict:

    url = f"{base_url.rstrip('/')}/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are Lab-Pocket, a MicroPython assistant "
                    "for ECE students. Give accurate, simple and "
                    "practical technical explanations."
                ),
            },
            {
                "role": "user",
                "content": f"Board: {board}\nQuestion: {question}",
            },
        ],
    }

    async with httpx.AsyncClient(
        timeout=settings.timeout_seconds
    ) as client:

        response = await client.post(
            url,
            headers=headers,
            json=payload,
        )

        response.raise_for_status()
        data = response.json()

    answer = data["choices"][0]["message"]["content"]
    usage = data.get("usage", {})

    return {
        "answer": answer,
        "model_used": model,
        "input_tokens": usage.get("prompt_tokens", 0),
        "output_tokens": usage.get("completion_tokens", 0),
        "total_tokens": usage.get("total_tokens", 0),
    }


async def generate_answer(
    settings: Settings,
    board: str,
    question: str,
) -> dict:

    providers = [
        (
            settings.primary_api_key,
            settings.primary_base_url,
            settings.primary_model,
        ),
        (
            settings.fallback_api_key,
            settings.fallback_base_url,
            settings.fallback_model,
        ),
    ]

    errors = []

    for api_key, base_url, model in providers:

        if not api_key:
            continue

        try:
            return await call_provider(
                settings,
                api_key,
                base_url,
                model,
                board,
                question,
            )

        except httpx.HTTPStatusError as error:
            print("API STATUS:", error.response.status_code)
            print("API ERROR:", error.response.text[:1000])
            errors.append(model)
            continue

        except (
            httpx.HTTPError,
            KeyError,
            IndexError,
            TypeError,
            ValueError,
        ) as error:
            print("API ERROR TYPE:", type(error).__name__)
            print("API ERROR:", str(error))
            errors.append(model)
            continue

    raise RuntimeError(
        "All configured LLM providers failed or no API key is configured."
    )
