

import re
from datetime import date

from pydantic.functional_validators import field_validator
from pydantic.main import BaseModel

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

    @field_validator("happened_at")
    @classmethod
    def happened_at_not_future(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("Date cannot be in the future.")
        return v

    @field_validator("description")
    @classmethod
    def description_stripped(cls, v: str) -> str:
        return v.strip()


class MilestoneUpdateDTO(MilestoneCreateDTO):
    tags: str = ""
