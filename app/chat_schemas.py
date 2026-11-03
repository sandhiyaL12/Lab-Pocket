from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    board: str = Field(..., min_length=1, description="Supported boards: ESP32, Raspberry Pi Pico")

    question: str = Field(..., min_length=3, description="User's technical question")

    @field_validator("board")
    @classmethod
    def validate_board(cls, value):
        supported_boards = {
            "esp32": "ESP32",
            "raspberry pi pico": "Raspberry Pi Pico",
            "pico": "Raspberry Pi Pico",
            "rp2": "Raspberry Pi Pico",
            "rp2040": "Raspberry Pi Pico",
        }

        normalized = " ".join(value.split()).casefold()

        if normalized not in supported_boards:
            raise ValueError("Unsupported board. Choose ESP32 or Raspberry Pi Pico.")

        return supported_boards[normalized]


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
    total_cost_usd: float = 0
