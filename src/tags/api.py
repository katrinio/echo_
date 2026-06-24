import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.templating import Jinja2Templates

from src.milestones.services import group_by_day
from src.orm.tag import Tag

router = APIRouter()
_TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=_TEMPLATES_DIR)
logger = logging.getLogger(__name__)


def _asset_version(rel_path: str) -> int:
    return int((_TEMPLATES_DIR.parent / "static" / rel_path).stat().st_mtime)


templates.env.globals["asset_version"] = _asset_version


@router.get("/tags/{tag_name}")
def tag_page(request: Request, tag_name: str):
    logger.debug("Requested tag page for tag_name=%s", tag_name)
    tag = Tag.get_by_name(tag_name.upper())
    if tag is None:
        logger.debug("Tag not found for tag_name=%s", tag_name)
        raise HTTPException(status_code=404, detail="Tag not found")

    milestones = list(tag.milestones)
    logger.debug(
        "Tag found for tag_name=%s milestone_count=%s", tag_name, len(milestones)
    )

    return templates.TemplateResponse(
        request,
        "tags/tag.html",
        {
            "tag": tag,
            "grouped_milestones": group_by_day(milestones),
        },
    )
