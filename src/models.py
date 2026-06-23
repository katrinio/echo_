from datetime import UTC, date, datetime
import re
from typing import Sequence

from sqlalchemy import Date, DateTime, String, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from src.database import engine


class Base(DeclarativeBase):
    pass


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

    @classmethod
    def add(cls, *, title: str, slug: str, happened_at: date, description: str = "") -> "Milestone":
        with Session(engine) as session:
            milestone = cls(title=title, slug=slug, happened_at=happened_at, description=description)
            session.add(milestone)
            session.commit()
            session.refresh(milestone)
            return milestone

    @classmethod
    def create_with_title(
        cls,
        *,
        title: str,
        happened_at: date,
        description: str = "",
    ) -> "Milestone":
        base_slug = cls.slug_from_title(title)
        slug = base_slug

        with Session(engine) as session:
            suffix = 1
            while session.execute(select(cls).where(cls.slug == slug)).scalars().first() is not None:
                suffix += 1
                slug = f"{base_slug}_{suffix}"

            milestone = cls(
                title=title,
                slug=slug,
                happened_at=happened_at,
                description=description,
            )
            session.add(milestone)
            session.commit()
            session.refresh(milestone)
            return milestone

    @classmethod
    def all(cls) -> Sequence["Milestone"]:
        with Session(engine) as session:
            return session.execute(select(cls)).scalars().all()

    @classmethod
    def get_by_slug(cls, slug: str) -> "Milestone | None":
        with Session(engine) as session:
            return session.execute(select(cls).where(cls.slug == slug)).scalars().first()

    @staticmethod
    def slug_from_title(title: str) -> str:
        slug = title.strip().upper()
        slug = re.sub(r"[^A-Z0-9]+", "_", slug)
        slug = re.sub(r"_+", "_", slug)
        return slug.strip("_")
