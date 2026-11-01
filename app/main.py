
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException

from app.config import Settings, get_settings
from app.chat_schemas import (
    ChatRequest,
    ChatResponse,
    UsageResponse,
)
from app.llm import generate_answer

app = FastAPI(
    title="Lab-Pocket API",
    version="0.2.0",
)

SettingsDep = Annotated[Settings, Depends(get_settings)]

usage_stats = {
    "total_requests": 0,
    "total_input_tokens": 0,
    "total_output_tokens": 0,
    "total_tokens": 0,
}


@app.get("/health")
def health(settings: SettingsDep) -> dict:
    return {
        "status": "ok",
        "app": settings.app_name,
        "environment": settings.environment,
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    settings: SettingsDep,
) -> ChatResponse:

    try:
        result = await generate_answer(
            settings,
            request.board,
            request.question,
        )

    except RuntimeError as error:
        raise HTTPException(
            status_code=502,
            detail=str(error),
        ) from error

    usage_stats["total_requests"] += 1
    usage_stats["total_input_tokens"] += result["input_tokens"]
    usage_stats["total_output_tokens"] += result["output_tokens"]
    usage_stats["total_tokens"] += result["total_tokens"]

    return ChatResponse(
        board=request.board,
        answer=result["answer"],
        model_used=result["model_used"],
        input_tokens=result["input_tokens"],
        output_tokens=result["output_tokens"],
        total_tokens=result["total_tokens"],
    )


@app.get("/usage", response_model=UsageResponse)
def usage() -> UsageResponse:
    return UsageResponse(**usage_stats)
