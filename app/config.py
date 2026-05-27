"""LeafLens API configuration via pydantic-settings."""

import logging
import sys

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed configuration — every env var is a field."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Supabase (auth verification)
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_jwks_url: str = ""  # auto-derived if empty

    # ThingsBoard
    tb_url: str = "http://localhost:8080"
    tb_api_key: str = ""
    tb_username: str = ""
    tb_password: str = ""

    # PostgreSQL
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/leaflens"

    # App
    debug: bool = False
    cors_origins: list[str] = ["http://localhost:3000"]
    ws_keepalive_interval: int = 30
    sentry_dsn: str = ""

    @model_validator(mode="after")
    def validate_required_fields(self) -> "Settings":
        """Fail fast on startup if critical env vars are missing."""
        missing = []
        if not self.tb_api_key:
            missing.append("TB_API_KEY")
        if not self.supabase_url and not self.debug:
            missing.append("SUPABASE_URL")
        if missing and not self.debug:
            logging.critical(
                f"FATAL: Missing required environment variables: {chr(44).join(missing)}",
            )
            sys.exit(1)
        return self

    @property
    def jwks_url(self) -> str:
        """Supabase JWKS endpoint — auto-derived from project URL."""
        if self.supabase_jwks_url:
            return self.supabase_jwks_url
        return f"{self.supabase_url}/auth/v1/.well-known/jwks.json"

    @property
    def tb_ws_url(self) -> str:
        """ThingsBoard WebSocket URL."""
        return self.tb_url.replace("http", "ws").rstrip("/") + "/api/ws"


_settings: Settings | None = None


def get_settings() -> Settings:
    """Singleton — avoids re-reading .env on every request."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
