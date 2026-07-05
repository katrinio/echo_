from fastapi import APIRouter, Request, Query
from fastapi.responses import PlainTextResponse, RedirectResponse
from fastapi.responses import JSONResponse

from src.features.milestones.services import group_by_year_and_month
from src.features.terminal.commands import COMMANDS
from src.orm.milestone import Milestone
from src.web.templates import templates

router = APIRouter()


@router.get("/terminal/commands")
def terminal_commands():
    return JSONResponse(
        [
            {
                "command": command.autocomplete_value,
                "description": command.description,
            }
            for command in COMMANDS
        ]
    )


@router.get("/help")
def help_page(request: Request):
    return templates.TemplateResponse(
        request,
        "terminal/help.html",
        {"commands": COMMANDS},
    )


@router.get("/random")
def random_page():
    milestone = Milestone.get_random()
    if milestone is None:
        return PlainTextResponse("No milestones found.")
    return RedirectResponse(url=f"/milestones/{milestone.slug}", status_code=303)


@router.get("/tree")
def tree_page(request: Request):
    return templates.TemplateResponse(
        request,
        "terminal/tree.html",
        {"tree": group_by_year_and_month(Milestone.all())},
    )


@router.get("/search")
def search_page(request: Request, q: str = Query(default="")):
    query = q.strip()
    results = Milestone.search(query)

    return templates.TemplateResponse(
        request,
        "terminal/search.html",
        {
            "query": query,
            "results": results,
        },
    )
