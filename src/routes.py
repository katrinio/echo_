from collections import OrderedDict
from collections.abc import Sequence
from datetime import date
from pathlib import Path

from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from src.models import Milestone

router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")


def _group_by_day(milestones: Sequence[Milestone]) -> OrderedDict[str, list[Milestone]]:
    grouped: dict[str, list[Milestone]] = {}
    for m in milestones:
        day = str(m.happened_at)
        grouped.setdefault(day, []).append(m)
    return OrderedDict(sorted(grouped.items(), reverse=True))


@router.get("/")
def index(request: Request):
    return templates.TemplateResponse(
        request,
        "index.html",
        {"grouped_milestones": _group_by_day(Milestone.all())},
    )


@router.get("/new")
def new_milestone(request: Request):
    return templates.TemplateResponse(request, "new.html", {})


@router.post("/new")
def create_milestone(
    title: str = Form(),
    happened_at: date = Form(),
    description: str = Form(default=""),
):
    Milestone.create_with_title(title=title, happened_at=happened_at, description=description)
    return RedirectResponse(url="/", status_code=303)


@router.get("/milestones/{slug}")
def milestone(request: Request, slug: str):
    return templates.TemplateResponse(
        request,
        "milestone.html",
        {"milestone": Milestone.get_by_slug(slug)},
    )
