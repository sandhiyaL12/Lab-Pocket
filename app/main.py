import json
import logging
import time
from collections.abc import AsyncIterator
from contextlib import aclosing
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import PlainTextResponse, StreamingResponse
from starlette.middleware.gzip import GZipMiddleware

from app.chat_schemas import ChatRequest, ChatResponse, UsageResponse
from app.config import Settings, get_settings
from app.cost import log_call
from app.llm import generate_answer, generate_answer_stream

logger = logging.getLogger(__name__)
MAX_CHAT_RESPONSE_BYTES = 4999
STREAM_EVENT_RESERVE_BYTES = 512


app = FastAPI(
    title="Lab-Pocket API",
    version="0.2.0",
)
app.add_middleware(GZipMiddleware, minimum_size=1)

SettingsDep = Annotated[Settings, Depends(get_settings)]


def _fit_response_size(response: ChatResponse) -> ChatResponse:
    if len(response.model_dump_json().encode("utf-8")) < MAX_CHAT_RESPONSE_BYTES + 1:
        return response

    marker = "\n[Answer shortened to fit the 5 KB response limit.]"
    low, high = 0, len(response.answer)
    best = response.model_copy(update={"answer": marker.strip()})
    while low <= high:
        midpoint = (low + high) // 2
        candidate = response.model_copy(update={"answer": response.answer[:midpoint].rstrip() + marker})
        if len(candidate.model_dump_json().encode("utf-8")) < MAX_CHAT_RESPONSE_BYTES + 1:
            best = candidate
            low = midpoint + 1
        else:
            high = midpoint - 1
    return best


@app.get("/")
def root():
    return {
        "app": "Lab-Pocket",
        "message": "Welcome to Lab-Pocket API",
    }


@app.get("/health")
def health(settings: SettingsDep):
    return {
        "status": "ok",
        "app": settings.app_name,
        "environment": settings.environment,
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    settings: SettingsDep,
    text_only: bool = False,
):
    start_time = time.perf_counter()

    try:
        result = await generate_answer(
            settings=settings,
            board=request.board,
            question=request.question,
        )
    except RuntimeError as error:
        raise HTTPException(
            status_code=502,
            detail=str(error),
        ) from error

    latency_ms = (time.perf_counter() - start_time) * 1000
    input_tokens = result.get("input_tokens", 0)
    output_tokens = result.get("output_tokens", 0)
    usage = {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "estimated": result.get("estimated", False),
    }
    log_call(
        settings.cost_log_path,
        provider=result["provider"],
        model=result["model_used"],
        usage=usage,
        latency_ms=latency_ms,
        price_in_per_m=result["input_cost_per_million"],
        price_out_per_m=result["output_cost_per_million"],
        ok=True,
        fallback_used=result["provider"] == "fallback",
    )

    response = _fit_response_size(
        ChatResponse(
            board=request.board,
            answer=result["answer"],
            model_used=result["model_used"],
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=result.get(
                "total_tokens",
                input_tokens + output_tokens,
            ),
        )
    )
    if text_only:
        return PlainTextResponse(response.answer)
    return response


@app.get("/usage", response_model=UsageResponse)
def usage(settings: SettingsDep):
    from pathlib import Path

    log_path = Path(settings.cost_log_path)
    if not log_path.exists():
        return UsageResponse()

    total_requests = 0
    total_input_tokens = 0
    total_output_tokens = 0
    total_cost_usd = 0.0

    with log_path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            try:
                record = json.loads(line)
                if not isinstance(record, dict):
                    raise TypeError("log record is not a JSON object")
                total_requests += 1
                total_input_tokens += record.get("input_tokens", 0)
                total_output_tokens += record.get("output_tokens", 0)
                total_cost_usd += record.get("cost_usd", 0)
            except (json.JSONDecodeError, TypeError, AttributeError) as error:
                logger.warning("Skipping malformed cost log line %s: %s", line_number, error)
                continue

    return UsageResponse(
        total_requests=total_requests,
        total_input_tokens=total_input_tokens,
        total_output_tokens=total_output_tokens,
        total_tokens=total_input_tokens + total_output_tokens,
        total_cost_usd=round(total_cost_usd, 10),
    )


@app.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    settings: SettingsDep,
) -> StreamingResponse:
    async def events() -> AsyncIterator[str]:
        start_time = time.perf_counter()
        sent_bytes = 0
        try:
            async with aclosing(
                generate_answer_stream(
                    settings=settings,
                    board=request.board,
                    question=request.question,
                )
            ) as answer_events:
                async for event in answer_events:
                    if event["type"] == "delta":
                        text = json.dumps(event["text"], ensure_ascii=False)
                        frame = f"event: token\ndata: {text}\n\n"
                        frame_size = len(frame.encode("utf-8"))
                        if sent_bytes + frame_size + STREAM_EVENT_RESERVE_BYTES >= MAX_CHAT_RESPONSE_BYTES:
                            yield (
                                "event: error\n"
                                'data: {"detail":"Answer shortened to fit the 5 KB stream limit."}\n\n'
                            )
                            return
                        sent_bytes += frame_size
                        yield frame
                    elif event["type"] == "usage":
                        elapsed_ms = (time.perf_counter() - start_time) * 1000
                        log_call(
                            settings.cost_log_path,
                            provider=event["provider"],
                            model=event["model_used"],
                            usage=event,
                            latency_ms=elapsed_ms,
                            price_in_per_m=event["input_cost_per_million"],
                            price_out_per_m=event["output_cost_per_million"],
                            ok=True,
                            fallback_used=event["provider"] == "fallback",
                        )
                        done = {
                            "board": request.board,
                            "model_used": event["model_used"],
                            "input_tokens": event["input_tokens"],
                            "output_tokens": event["output_tokens"],
                            "total_tokens": event["total_tokens"],
                        }
                        frame = f"event: done\ndata: {json.dumps(done)}\n\n"
                        sent_bytes += len(frame.encode("utf-8"))
                        yield frame
        except RuntimeError as error:
            logger.warning("Chat stream failed: %s", error)
            yield f"event: error\ndata: {json.dumps({'detail': str(error)})}\n\n"

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
