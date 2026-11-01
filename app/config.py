
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

    app_name: str = "Lab-Pocket"
    environment: str = "local"

    primary_api_key: str | None = None
    primary_base_url: str = "https://api.openai.com/v1"
    primary_model: str = "gpt-4o-mini"

    fallback_api_key: str | None = None
    fallback_base_url: str = "https://api.openai.com/v1"
    fallback_model: str = "gpt-4o-mini"

    timeout_seconds: int = 30


@lru_cache
def get_settings() -> Settings:
    return Settings()
