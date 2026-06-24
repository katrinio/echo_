from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.database import Base, engine
from src.milestones.api import router as milestones_router
from src.tags.api import router as tags_router

SRC = Path(__file__).parent

app = FastAPI()
app.mount("/static", StaticFiles(directory=SRC / "static"), name="static")
app.include_router(milestones_router)
app.include_router(tags_router)


@app.on_event("startup")
def on_startup() -> None:
    import src.orm.milestone  # noqa: F401
    import src.orm.tag  # noqa: F401
    Base.metadata.create_all(engine)
