from collections import OrderedDict
from collections.abc import Sequence
from datetime import date
from pathlib import Path

from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError

from src.milestones.dto import MilestoneCreateDTO, MilestoneUpdateDTO
from orm.milestone import Milestone

router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")


def _group_by_day(milestones: Sequence[Milestone]) -> OrderedDict[str, list[Milestone]]:
    grouped: dict[str, list[Milestone]] = {}
    for m in milestones:
        day = str(m.happened_at)
        grouped.setdefault(day, []).append(m)
    return OrderedDict(sorted(grouped.items(), reverse=True))


def _first_error(exc: ValidationError) -> str:
    return exc.errors()[0]["msg"].removeprefix("Value error, ")


@router.get("/")
def index(request: Request):
    return templates.TemplateResponse(
        request,
        "milestones/index.html",
        {"grouped_milestones": _group_by_day(Milestone.all())},
    )


@router.get("/new")
def new_milestone(request: Request):
    return templates.TemplateResponse(
        request,
        "milestones/new.html",
        {"today": date.today().isoformat()},
    )


@router.post("/new")
def create_milestone(
    request: Request,
    title: str = Form(),
    happened_at: date = Form(),
    description: str = Form(default=""),
):
    try:
        dto = MilestoneCreateDTO(title=title, happened_at=happened_at, description=description)
    except ValidationError as exc:
        return templates.TemplateResponse(
            request,
            "milestones/new.html",
            {"error": _first_error(exc), "today": date.today().isoformat()},
            status_code=422,
        )

    Milestone.create_with_title(
        title=dto.title,
        happened_at=dto.happened_at,
        description=dto.description,
    )
    return RedirectResponse(url="/", status_code=303)


@router.get("/milestones/{slug}")
def milestone(request: Request, slug: str):
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
        {"milestone": Milestone.get_by_slug(slug)},
    )


@router.post("/milestones/{slug}/edit")
def update_milestone(
    request: Request,
    slug: str,
    title: str = Form(),
    happened_at: date = Form(),
    description: str = Form(default=""),
):
    try:
        dto = MilestoneUpdateDTO(title=title, happened_at=happened_at, description=description)
    except ValidationError as exc:
        return templates.TemplateResponse(
            request,
            "milestones/edit.html",
            {
                "milestone": Milestone.get_by_slug(slug),
                "error": _first_error(exc),
            },
            status_code=422,
        )

    updated = Milestone.update_by_slug(
        slug,
        title=dto.title,
        happened_at=dto.happened_at,
        description=dto.description,
    )
    return RedirectResponse(url=f"/milestones/{updated.slug}", status_code=303)
