from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "LeadGen Scraper Pro"
    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"
    backend_cors_origins: List[str] = Field(default_factory=lambda: ["http://localhost:5173"])
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/leadgen_scraper"
    google_places_api_key: str | None = None
    scraper_min_delay_seconds: float = 1.0
    scraper_max_delay_seconds: float = 3.0
    scraper_max_retries: int = 3

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator("backend_cors_origins", mode="before")
    @classmethod
    def split_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
