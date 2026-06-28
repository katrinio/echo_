from typing import Annotated

from fastapi import APIRouter, Form, Query, Request

from .security import (
    create_login_response,
    create_logout_response,
    verify_password,
)
from ...web.templates import templates

router = APIRouter()


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
