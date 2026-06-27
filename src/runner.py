import os

import uvicorn

from src.config import settings


def run() -> None:
    os.environ["DATABASE_URL"] = settings.database_url
    uvicorn.run("src.app:app", host="127.0.0.1", port=8000)
