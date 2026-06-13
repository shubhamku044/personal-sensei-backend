"""Application configuration."""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings, loaded from the environment (and an optional .env file)."""

    model_config = SettingsConfigDict(env_file=".env", env_prefix="APP_", extra="ignore")

    app_name: str = "Personal Sensei API"
    version: str = "0.1.0"
    environment: str = "development"

    # LLM / agent configuration.
    # The API key is read from the standard OPENAI_API_KEY env var (no APP_
    # prefix); everything else uses the APP_ prefix.
    openai_api_key: str | None = Field(default=None, validation_alias="OPENAI_API_KEY")
    openai_model: str = "gpt-4o-mini"
    agent_temperature: float = 0.0
    agent_max_tokens: int = 1024

    # Comma-separated list of origins allowed to call the API (CORS).
    cors_allow_origins: list[str] = ["http://localhost:3000"]


@lru_cache
def get_settings() -> Settings:
    """Return a cached `Settings` instance."""
    return Settings()
