from __future__ import annotations

from datetime import UTC, date, datetime
from typing import TYPE_CHECKING, Sequence

from sqlalchemy import Date, DateTime, String, select
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from src.database import Base, engine
from src.orm.milestone_tags import milestone_tags
from src.milestones.helpers import slug_from_title, slug_with_suffix

if TYPE_CHECKING:
    from src.orm.tag import Tag


class Milestone(Base):
    __tablename__ = "milestones"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    description: Mapped[str] = mapped_column(String, server_default="")
    happened_at: Mapped[date] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    tags: Mapped[list[Tag]] = relationship(
        "Tag",
        secondary=milestone_tags,
        back_populates="milestones",
        lazy="selectin",
    )

    @classmethod
    def create_with_title(
        cls,
        *,
        title: str,
        happened_at: date,
        description: str = "",
        tags: list[str] | None = None,
    ) -> Milestone:
        from src.orm.tag import Tag as TagModel

        base_slug = slug_from_title(title)
        slug = base_slug

        with Session(engine) as session:
            suffix = 1
            while session.execute(select(cls).where(cls.slug == slug)).scalars().first() is not None:
                suffix += 1
                slug = slug_with_suffix(base_slug, suffix)

            milestone = cls(
                title=title,
                slug=slug,
                happened_at=happened_at,
                description=description,
            )
            if tags:
                milestone.tags = TagModel.get_or_create_many(session, tags)
            session.add(milestone)
            session.commit()
            session.refresh(milestone)
            return milestone

    @classmethod
    def all(cls) -> Sequence[Milestone]:
        with Session(engine) as session:
            return session.execute(select(cls)).scalars().all()

    @classmethod
    def get_by_slug(cls, slug: str) -> Milestone | None:
        with Session(engine) as session:
            return session.execute(select(cls).where(cls.slug == slug)).scalars().first()

    @classmethod
    def update_by_slug(
        cls,
        slug: str,
        *,
        title: str,
        happened_at: date,
        description: str = "",
        tags: list[str] | None = None,
    ) -> Milestone:
        from src.orm.tag import Tag as TagModel

        with Session(engine) as session:
            milestone = session.scalar(select(cls).where(cls.slug == slug))
            if milestone is None:
                raise ValueError(f"Milestone not found: {slug}")

            milestone.title = title
            milestone.happened_at = happened_at
            milestone.description = description
            milestone.tags = TagModel.get_or_create_many(session, tags or [])

            session.commit()
            session.refresh(milestone)
            return milestone
