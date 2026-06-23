from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.core.database import engine
from orm.milestone import Base
from src.milestones.routes import router

SRC = Path(__file__).parent.parent

app = FastAPI()
app.mount("/static", StaticFiles(directory=SRC / "static"), name="static")
app.include_router(router)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(engine)
