from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from src.milestones.commands import COMMANDS

router = APIRouter()

_TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=_TEMPLATES_DIR)


def _asset_version(rel_path: str) -> int:
    return int((_TEMPLATES_DIR.parent / "static" / rel_path).stat().st_mtime)


templates.env.globals["asset_version"] = _asset_version


@router.get("/help")
def help_page(request: Request):
    return templates.TemplateResponse(
        request,
        "terminal/help.html",
        {"commands": COMMANDS},
    )
