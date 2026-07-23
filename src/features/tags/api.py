import logging

from fastapi import APIRouter, HTTPException, Request

from src.features.milestones.services import group_by_day
from src.orm.tag import Tag
from src.web.templates import templates

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/tags/{tag_name}")
def tag_page(request: Request, tag_name: str):
    logger.info("Tag page opened: tag=%s", tag_name.upper())
    tag = Tag.get_by_name(tag_name.upper())
    if tag is None:
        logger.warning("Tag not found: tag=%s", tag_name.upper())
        raise HTTPException(status_code=404, detail="Tag not found")

    milestones = list(tag.milestones)
    logger.info(
        "Tag loaded: tag=%s milestones=%s", tag.name, len(milestones)
    )

    return templates.TemplateResponse(
        request,
        "tags/tag.html",
        {
            "tag": tag,
            "grouped_milestones": group_by_day(milestones),
        },
    )


@router.get("/tags")
def tags_page(request: Request):
    tags = Tag.all_with_counts()
    logger.info("Tags page opened: tags=%s", len(tags))
    return templates.TemplateResponse(
        request,
        "tags/tags.html",
        {
            "tags": tags,
        },
    )
