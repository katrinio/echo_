from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

from src.database import Base, engine
from src.features.milestones.api import router as milestones_router
from src.features.terminal.api import router as terminal_router
from src.features.tags.api import router as tags_router
from src.features.auth.api import router as auth_router
from src.features.auth.middleware import AuthMiddleware

SRC = Path(__file__).parent


@asynccontextmanager
async def lifespan(app: FastAPI):
    import src.orm.milestone  # noqa: F401
    import src.orm.tag  # noqa: F401
    Base.metadata.create_all(engine)
    yield


app = FastAPI(
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)


@app.middleware("http")
async def cache_control(request: Request, call_next):
    response = await call_next(request)

    path = request.scope.get("path", request.url.path)
    root_path = request.scope.get("root_path", "")
    if root_path and path.startswith(root_path):
        path = path.removeprefix(root_path) or "/"

    if path.startswith("/static/"):
        response.headers.setdefault(
            "Cache-Control",
            "public, max-age=31536000, immutable",
        )
        return response

    content_type = response.headers.get("content-type", "")
    if content_type.startswith("text/html"):
        response.headers.setdefault("Cache-Control", "no-store")

    return response


app.add_middleware(AuthMiddleware)
app.include_router(auth_router)
app.mount("/static", StaticFiles(directory=SRC / "static"), name="static")
app.include_router(milestones_router)
app.include_router(terminal_router)
app.include_router(tags_router)
