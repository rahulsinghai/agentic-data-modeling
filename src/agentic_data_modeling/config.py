"""Application configuration via Pydantic Settings."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="ADM_", env_file=".env", extra="ignore", populate_by_name=True
    )

    # Read from OPENAI_API_KEY (standard name), not ADM_OPENAI_API_KEY
    openai_api_key: str = Field(default="", validation_alias="OPENAI_API_KEY")
    model: str = "gpt-4o-mini"
    output_dir: Path = Path("output")
    max_tokens: int = 8192
    temperature: float = 0.0


def get_settings(**overrides: object) -> Settings:
    return Settings(**overrides)  # type: ignore[arg-type]
