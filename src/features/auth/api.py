import logging
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Form, Query, Request
from fastapi.responses import FileResponse

from .security import (
    create_login_response,
    create_logout_response,
    verify_password,
)
from ...web.templates import templates

router = APIRouter()
logger = logging.getLogger(__name__)

_STATIC = Path(__file__).parent.parent.parent / "static"


@router.get("/robots.txt", include_in_schema=False)
def robots():
    return FileResponse(_STATIC / "robots.txt", media_type="text/plain")


@router.get("/health")
def health(request: Request):
    logger.info("Health page opened")
    return templates.TemplateResponse(
        request,
        "auth/health.html",
    )


@router.get("/login")
def login_page(
    request: Request,
    next_url: Annotated[str, Query(alias="next")] = "/",
):
    logger.info("Login page opened: next=%s", next_url)
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
        logger.warning("Login failed: next=%s", next_url)
        return templates.TemplateResponse(
            request,
            "auth/login.html",
            {
                "next_url": next_url,
                "error": "Authentication failed",
            },
            status_code=401,
        )

    logger.info("Login succeeded: next=%s", next_url)
    return create_login_response(next_url)


@router.get("/logout")
def logout():
    logger.info("Logout succeeded")
    return create_logout_response()
