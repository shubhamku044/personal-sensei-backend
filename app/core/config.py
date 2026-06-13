"""Application configuration."""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings, loaded from the environment (and an optional .env file)."""

    model_config = SettingsConfigDict(env_file=".env", env_prefix="APP_", extra="ignore")

    app_name: str = "Personal Sensei API"
    version: str = "0.1.0"
    environment: str = "development"


@lru_cache
def get_settings() -> Settings:
    """Return a cached `Settings` instance."""
    return Settings()
