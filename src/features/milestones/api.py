from datetime import date

from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse
from pydantic import ValidationError

from src.features.milestones.dto import (
    MilestoneCreateDTO,
    MilestoneUpdateDTO,
    today_in_timezone,
    validate_happened_at_not_future,
)
from src.features.milestones.services import group_by_day
from src.orm.milestone import Milestone
from src.orm.tag import Tag
from src.web.templates import templates

router = APIRouter()


def _first_error(exc: ValidationError) -> str:
    return exc.errors()[0]["msg"].removeprefix("Value error, ")


@router.get("/")
def index(request: Request):
    return templates.TemplateResponse(
        request,
        "milestones/index.html",
        {"grouped_milestones": group_by_day(Milestone.all())},
    )


@router.get("/new")
def new_milestone(request: Request):
    return templates.TemplateResponse(
        request,
        "milestones/new.html",
        {
            "today": today_in_timezone(None).isoformat(),
            "all_tags": Tag.all(),
        },
    )


@router.post("/new")
def create_milestone(
    request: Request,
    title: str = Form(),
    happened_at: date = Form(),
    description: str = Form(default=""),
    tags: str = Form(default=""),
    timezone: str = Form(default=""),
):
    try:
        validate_happened_at_not_future(happened_at, timezone or None)
        dto = MilestoneCreateDTO(
            title=title, happened_at=happened_at, description=description, tags=tags
        )
    except ValidationError as exc:
        return templates.TemplateResponse(
            request,
            "milestones/new.html",
            {
                "error": _first_error(exc),
                "today": today_in_timezone(timezone or None).isoformat(),
                "all_tags": Tag.all(),
            },
            status_code=422,
        )
    except ValueError as exc:
        return templates.TemplateResponse(
            request,
            "milestones/new.html",
            {
                "error": str(exc),
                "today": today_in_timezone(timezone or None).isoformat(),
                "all_tags": Tag.all(),
            },
            status_code=422,
        )

    Milestone.create_with_title(
        title=dto.title,
        happened_at=dto.happened_at,
        description=dto.description,
        tags=dto.tags.split() if dto.tags else [],
    )
    return RedirectResponse(url="/", status_code=303)


@router.get("/milestones/{slug}")
def milestone_detail(request: Request, slug: str):
    return templates.TemplateResponse(
        request,
        "milestones/detail.html",
        {"milestone": Milestone.get_by_slug(slug)},
    )


@router.get("/milestones/{slug}/edit")
def edit_milestone(request: Request, slug: str):
    return templates.TemplateResponse(
        request,
        "milestones/edit.html",
        {
            "milestone": Milestone.get_by_slug(slug),
            "all_tags": Tag.all(),
        },
    )


@router.post("/milestones/{slug}/edit")
def update_milestone(
    request: Request,
    slug: str,
    title: str = Form(),
    happened_at: date = Form(),
    description: str = Form(default=""),
    tags: str = Form(default=""),
    timezone: str = Form(default=""),
):
    try:
        validate_happened_at_not_future(happened_at, timezone or None)
        dto = MilestoneUpdateDTO(
            title=title, happened_at=happened_at, description=description, tags=tags
        )
    except ValidationError as exc:
        return templates.TemplateResponse(
            request,
            "milestones/edit.html",
            {
                "milestone": Milestone.get_by_slug(slug),
                "error": _first_error(exc),
                "all_tags": Tag.all(),
            },
            status_code=422,
        )
    except ValueError as exc:
        return templates.TemplateResponse(
            request,
            "milestones/edit.html",
            {
                "milestone": Milestone.get_by_slug(slug),
                "error": str(exc),
                "all_tags": Tag.all(),
            },
            status_code=422,
        )

    updated = Milestone.update_by_slug(
        slug,
        title=dto.title,
        happened_at=dto.happened_at,
        description=dto.description,
        tags=dto.tags.split() if dto.tags else [],
    )
    return RedirectResponse(url=f"/milestones/{updated.slug}", status_code=303)
