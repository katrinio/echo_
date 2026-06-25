from datetime import date
from pathlib import Path

from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError

from src.milestones.dto import MilestoneCreateDTO, MilestoneUpdateDTO
from src.milestones.helpers import parse_tags
from src.orm.milestone import Milestone
from src.milestones.services import group_by_day
from src.orm.tag import Tag

router = APIRouter()

_TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=_TEMPLATES_DIR)


def _asset_version(rel_path: str) -> int:
    return int((_TEMPLATES_DIR.parent / "static" / rel_path).stat().st_mtime)


templates.env.globals["asset_version"] = _asset_version


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
                "today": date.today().isoformat(),
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
):
    try:
        dto = MilestoneCreateDTO(
            title=title, happened_at=happened_at, description=description, tags=tags
        )
    except ValidationError as exc:
        return templates.TemplateResponse(
            request,
            "milestones/new.html",
            {
                "error": _first_error(exc),
                "today": date.today().isoformat(),
                "all_tags": Tag.all(),
            },
            status_code=422,
        )

    Milestone.create_with_title(
        title=dto.title,
        happened_at=dto.happened_at,
        description=dto.description,
        tags=parse_tags(dto.tags),
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
):
    try:
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

    updated = Milestone.update_by_slug(
        slug,
        title=dto.title,
        happened_at=dto.happened_at,
        description=dto.description,
        tags=parse_tags(dto.tags),
    )
    return RedirectResponse(url=f"/milestones/{updated.slug}", status_code=303)
