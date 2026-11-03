from typing import Literal

from pydantic import BaseModel, Field

from app.chat_schemas import ChatRequest, ChatResponse, UsageResponse


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str = Field(min_length=1)


__all__ = ["ChatMessage", "ChatRequest", "ChatResponse", "UsageResponse"]
