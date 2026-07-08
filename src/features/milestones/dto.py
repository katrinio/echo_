

import re
from datetime import UTC, date, datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic.functional_validators import field_validator
from pydantic.main import BaseModel

from src.features.milestones.helpers import parse_tags

_TITLE_RE = re.compile(r"^[A-Za-z0-9 .\-]+$")


class MilestoneCreateDTO(BaseModel):
    title: str
    happened_at: date
    description: str = ""
    tags: str = ""

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Title must not be empty.")
        if not _TITLE_RE.match(v):
            raise ValueError(
                "Title may only contain English letters, digits, spaces, dots and hyphens."
            )
        return v

    @field_validator("description")
    @classmethod
    def description_stripped(cls, v: str) -> str:
        return v.strip()

    @field_validator("tags")
    @classmethod
    def tags_are_valid(cls, v: str) -> str:
        return " ".join(parse_tags(v))


class MilestoneUpdateDTO(MilestoneCreateDTO):
    tags: str = ""


def today_in_timezone(timezone_name: str | None) -> date:
    if not timezone_name:
        return datetime.now(UTC).date()

    try:
        zone = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        return datetime.now(UTC).date()

    return datetime.now(zone).date()


def validate_happened_at_not_future(happened_at: date, timezone_name: str | None) -> None:
    if happened_at > today_in_timezone(timezone_name):
        raise ValueError("Date cannot be in the future for your timezone.")
