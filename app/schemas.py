from typing import Literal

from pydantic import BaseModel, Field

from app.chat_schemas import ChatRequest, ChatResponse, UsageResponse


class Citation(BaseModel):
    document: str
    page: int
    section: str = ""


class AskResponse(BaseModel):
    board: str
    answer: str
    model_used: str
    citations: list[Citation]


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str = Field(min_length=1)


__all__ = ["AskResponse", "Citation", "ChatMessage", "ChatRequest", "ChatResponse", "UsageResponse"]
