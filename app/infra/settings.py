from __future__ import annotations

from functools import lru_cache
from pydantic import BaseModel
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    github_token: str
    openai_api_key: str
    secret: str
    github_username: str
    port: int = 5000

    # Fallback provider
    aipipe_aki_key: str | None = None
    fallback_base_url: str = "https://aipipe.org/openai/v1"

    class Config:
        env_prefix = ""
        case_sensitive = False
        env_file = ".env"


class EnvSummary(BaseModel):
    github_username: str
    port: int


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # reads from environment and .env


def summarize_env() -> EnvSummary:
    s = get_settings()
    return EnvSummary(github_username=s.github_username, port=s.port)


def validate_required_env() -> None:
    s = get_settings()
    missing = []
    if not s.github_token:
        missing.append("GITHUB_TOKEN")
    if not s.openai_api_key:
        missing.append("OPENAI_API_KEY")
    if not s.secret:
        missing.append("SECRET")
    if not s.github_username:
        missing.append("GITHUB_USERNAME")

    if missing:
        print("\nERROR: Missing required environment variables:")
        for var in missing:
            print(f"  - {var}")
        raise SystemExit(1)

