from pathlib import Path

from sqlalchemy import create_engine

ROOT = Path(__file__).parent.parent.parent
DATABASE_URL = f"sqlite:///{ROOT / 'echo.db'}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

