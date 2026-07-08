import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_ROOT = Path(__file__).parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = f"sqlite:///{_ROOT / 'user_data' / 'echo.db'}"
    session_secret_key: str = ""
    echo_password: str = ""
    echo_username: str = "katrin"

    @property
    def is_production(self) -> bool:
        return os.getenv("ENVIRONMENT") == "production"


settings = Settings()
