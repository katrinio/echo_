from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.milestones.routes import router

SRC = Path(__file__).parent.parent

app = FastAPI()
app.mount("/static", StaticFiles(directory=SRC / "static"), name="static")
app.include_router(router)
