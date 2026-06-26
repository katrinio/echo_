import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_ROOT = Path(__file__).parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = f"sqlite:///{_ROOT / 'echo.db'}"
    session_secret_key: str = ""
    echo_password: str = ""

    @property
    def is_production(self) -> bool:
        return os.getenv("ENVIRONMENT") == "production"


settings = Settings()
