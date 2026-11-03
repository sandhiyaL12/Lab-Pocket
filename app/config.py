from functools import lru_cache

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    app_name: str = Field(
        default="Lab-Pocket",
        validation_alias="APP_NAME",
    )

    environment: str = Field(
        default="local",
        validation_alias="ENVIRONMENT",
    )

    llm_provider: str = Field(
        default="openai_compat",
        validation_alias="LLM_PROVIDER",
    )

    primary_api_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices("PRIMARY_API_KEY", "LLM_API_KEY"),
    )

    primary_base_url: str = Field(
        default="https://api.openai.com/v1",
        validation_alias=AliasChoices("PRIMARY_BASE_URL", "LLM_BASE_URL"),
    )

    primary_model: str = Field(
        default="gpt-4o-mini",
        validation_alias=AliasChoices("PRIMARY_MODEL", "LLM_MODEL"),
    )

    fallback_api_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices("FALLBACK_API_KEY", "LLM_FALLBACK_API_KEY"),
    )

    fallback_base_url: str = Field(
        default="https://api.openai.com/v1",
        validation_alias=AliasChoices("FALLBACK_BASE_URL", "LLM_FALLBACK_BASE_URL"),
    )

    fallback_model: str = Field(
        default="",
        validation_alias=AliasChoices("FALLBACK_MODEL", "LLM_FALLBACK_MODEL"),
    )

    timeout_seconds: float = Field(
        default=30,
        gt=0,
        validation_alias=AliasChoices("TIMEOUT_SECONDS", "LLM_TIMEOUT_SECONDS"),
    )

    max_retries: int = Field(
        default=1,
        ge=0,
        le=3,
        validation_alias="LLM_MAX_RETRIES",
    )

    retry_delay_seconds: float = Field(
        default=0.25,
        ge=0,
        validation_alias="LLM_RETRY_DELAY_SECONDS",
    )

    max_output_tokens: int = Field(
        default=700,
        ge=1,
        le=2048,
        validation_alias="LLM_MAX_OUTPUT_TOKENS",
    )

    primary_input_cost_per_million: float = Field(
        default=0,
        ge=0,
        validation_alias="PRIMARY_INPUT_COST_PER_MILLION",
    )

    primary_output_cost_per_million: float = Field(
        default=0,
        ge=0,
        validation_alias="PRIMARY_OUTPUT_COST_PER_MILLION",
    )

    fallback_input_cost_per_million: float = Field(
        default=0,
        ge=0,
        validation_alias="FALLBACK_INPUT_COST_PER_MILLION",
    )

    fallback_output_cost_per_million: float = Field(
        default=0,
        ge=0,
        validation_alias="FALLBACK_OUTPUT_COST_PER_MILLION",
    )

    cost_log_path: str = Field(
        default="data/cost_log.jsonl",
        validation_alias="COST_LOG_PATH",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
