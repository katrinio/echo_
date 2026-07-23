import logging

from fastapi import APIRouter, Request, Query
from fastapi.responses import PlainTextResponse, RedirectResponse
from fastapi.responses import JSONResponse

from src.features.milestones.services import group_by_year_and_month
from src.features.terminal.commands import COMMANDS
from src.orm.milestone import Milestone
from src.web.templates import templates

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/terminal/commands")
def terminal_commands():
    logger.info("Terminal commands requested: count=%s", len(COMMANDS))
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
    logger.info("Help page opened: commands=%s", len(COMMANDS))
    return templates.TemplateResponse(
        request,
        "terminal/help.html",
        {"commands": COMMANDS},
    )


@router.get("/random")
def random_page():
    milestone = Milestone.get_random()
    if milestone is None:
        logger.warning("Random milestone requested: no milestones found")
        return PlainTextResponse("No milestones found.")
    logger.info("Random milestone selected: slug=%s", milestone.slug)
    return RedirectResponse(url=f"/milestones/{milestone.slug}", status_code=303)


@router.get("/tree")
def tree_page(request: Request):
    tree = group_by_year_and_month(Milestone.all())
    year_count = len(tree)
    milestone_count = sum(
        len(entries)
        for months in tree.values()
        for days in months.values()
        for entries in days.values()
    )
    logger.info("Tree page opened: years=%s milestones=%s", year_count, milestone_count)
    return templates.TemplateResponse(
        request,
        "terminal/tree_year.html",
        {"tree": tree},
    )


@router.get("/search")
def search_page(request: Request, q: str = Query(default="")):
    query = q.strip()
    results = Milestone.search(query)
    logger.info("Search completed: query=%s results=%s", query or "<empty>", len(results))

    return templates.TemplateResponse(
        request,
        "terminal/search.html",
        {
            "query": query,
            "results": results,
        },
    )
