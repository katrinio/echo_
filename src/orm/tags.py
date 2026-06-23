

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.orm.base import Base
from src.orm.milestone_tags import milestone_tags

if TYPE_CHECKING:
    from src.orm.milestone import Milestone


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    milestones: Mapped[list["Milestone"]] = relationship(
        secondary=milestone_tags,
        back_populates="tags",
        lazy="selectin",
    )
