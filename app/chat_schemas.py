
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    board: str = Field(
        ...,
        min_length=1,
        description="MicroPython board name"
    )

    question: str = Field(
        ...,
        min_length=3,
        description="User's technical question"
    )


class ChatResponse(BaseModel):
    board: str
    answer: str
    model_used: str
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0


class UsageResponse(BaseModel):
    total_requests: int = 0
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_tokens: int = 0
