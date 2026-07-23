from datetime import date
import logging

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
logger = logging.getLogger(__name__)


def _first_error(exc: ValidationError) -> str:
    return exc.errors()[0]["msg"].removeprefix("Value error, ")


@router.get("/")
def index(request: Request):
    grouped = group_by_day(Milestone.all())
    group_count = len(grouped)
    milestone_count = sum(len(items) for items in grouped.values())
    logger.info(
        "Milestones index opened: groups=%s milestones=%s",
        group_count,
        milestone_count,
    )
    return templates.TemplateResponse(
        request,
        "milestones/index.html",
        {"grouped_milestones": grouped},
    )


@router.get("/new")
def new_milestone(request: Request):
    all_tags = Tag.all()
    logger.info("New milestone form opened: tags=%s", len(all_tags))
    return templates.TemplateResponse(
        request,
        "milestones/new.html",
        {
            "today": today_in_timezone(None).isoformat(),
            "all_tags": all_tags,
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
        logger.warning("Milestone creation failed validation: title=%s", title)
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
        logger.warning(
            "Milestone creation rejected: title=%s reason=%s",
            title,
            str(exc),
        )
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

    milestone = Milestone.create_with_title(
        title=dto.title,
        happened_at=dto.happened_at,
        description=dto.description,
        tags=dto.tags.split() if dto.tags else [],
    )
    logger.info(
        "Milestone created: slug=%s date=%s tags=%s",
        milestone.slug,
        milestone.happened_at.isoformat(),
        len(milestone.tags),
    )
    return RedirectResponse(url="/", status_code=303)


@router.get("/milestones/{slug}")
def milestone_detail(request: Request, slug: str):
    milestone = Milestone.get_by_slug(slug)
    logger.info("Milestone opened: slug=%s found=%s", slug, milestone is not None)
    return templates.TemplateResponse(
        request,
        "milestones/detail.html",
        {"milestone": milestone},
    )


@router.get("/milestones/{slug}/edit")
def edit_milestone(request: Request, slug: str):
    milestone = Milestone.get_by_slug(slug)
    all_tags = Tag.all()
    logger.info("Milestone edit form opened: slug=%s tags=%s", slug, len(all_tags))
    return templates.TemplateResponse(
        request,
        "milestones/edit.html",
        {
            "milestone": milestone,
            "all_tags": all_tags,
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
        logger.warning("Milestone update failed validation: slug=%s", slug)
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
        logger.warning(
            "Milestone update rejected: slug=%s reason=%s",
            slug,
            str(exc),
        )
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
    logger.info(
        "Milestone updated: old_slug=%s new_slug=%s date=%s tags=%s",
        slug,
        updated.slug,
        updated.happened_at.isoformat(),
        len(updated.tags),
    )
    return RedirectResponse(url=f"/milestones/{updated.slug}", status_code=303)
