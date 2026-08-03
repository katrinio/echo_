from pathlib import Path
import json
from typing import Annotated

from fastapi import APIRouter, Form, Query, Request
from fastapi.responses import FileResponse, JSONResponse

from .security import (
    create_login_response,
    create_logout_response,
    verify_password,
)
from ...web.templates import templates
from ...version import get_version_string

router = APIRouter()

_STATIC = Path(__file__).parent.parent.parent / "static"


@router.get("/robots.txt", include_in_schema=False)
def robots():
    return FileResponse(_STATIC / "robots.txt", media_type="text/plain")


@router.get("/static/site.webmanifest", include_in_schema=False)
@router.get("/manifest.webmanifest", include_in_schema=False)
def site_manifest(request: Request):
    manifest = json.loads((_STATIC / "site.webmanifest").read_text(encoding="utf-8"))
    version = get_version_string()
    for icon in manifest.get("icons", []):
        src = icon.get("src")
        if isinstance(src, str) and "?" not in src:
            icon["src"] = _manifest_static_url(request, src, version)
    return JSONResponse(
        manifest,
        headers={"Cache-Control": "no-cache"},
        media_type="application/manifest+json",
    )


@router.get("/sw.js", include_in_schema=False)
def service_worker():
    return FileResponse(
        _STATIC / "sw.js",
        media_type="text/javascript; charset=utf-8",
        headers={"Cache-Control": "no-cache"},
    )


def _manifest_static_url(request: Request, src: str, version: str) -> str:
    rel_path = src.removeprefix("/").removeprefix("static/")
    root_path = request.scope.get("root_path", "")
    path = request.app.url_path_for("static", path=rel_path)
    return f"{root_path}{path}?v={version}"


@router.get("/health")
def health(request: Request):
    return templates.TemplateResponse(
        request,
        "auth/health.html",
    )


@router.get("/login")
def login_page(
    request: Request,
    next_url: Annotated[str, Query(alias="next")] = "/",
):
    return templates.TemplateResponse(
        request,
        "auth/login.html",
        {
            "next_url": next_url,
        },
    )


@router.post("/login")
def login(
    request: Request,
    password: Annotated[str, Form()],
    next_url: Annotated[str, Form(alias="next")] = "/",
):
    if not verify_password(password):
        return templates.TemplateResponse(
            request,
            "auth/login.html",
            {
                "next_url": next_url,
                "error": "Authentication failed",
            },
            status_code=401,
        )

    return create_login_response(next_url)


@router.get("/logout")
def logout():
    return create_logout_response()
