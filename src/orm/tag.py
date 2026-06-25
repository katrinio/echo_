from __future__ import annotations

from typing import TYPE_CHECKING, Sequence

from sqlalchemy import String, func, select
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship
from sqlalchemy.orm import selectinload

from src.database import Base, engine
from src.orm.milestone_tags import milestone_tags

if TYPE_CHECKING:
    from src.orm.milestone import Milestone


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    milestones: Mapped[list[Milestone]] = relationship(
        "Milestone",
        secondary=milestone_tags,
        back_populates="tags",
        lazy="selectin",
    )

    @classmethod
    def all(cls) -> Sequence["Tag"]:
        with Session(engine) as session:
            return session.execute(
                select(cls).order_by(cls.name)
            ).scalars().all()

    @classmethod
    def all_with_counts(cls) -> list[tuple[str, int]]:
        from src.orm.milestone import Milestone

        with Session(engine) as session:
            rows = session.execute(
                select(Tag.name, func.count(Milestone.id))
                .outerjoin(Tag.milestones)
                .group_by(Tag.id)
                .order_by(Tag.name)
            ).all()
            return [(name, int(count)) for name, count in rows]

    @classmethod
    def get_by_name(cls, name: str) -> Tag | None:
        with Session(engine) as session:
            return (
                session.execute(
                    select(cls)
                    .options(selectinload(cls.milestones))
                    .where(cls.name == name)
                )
                .scalars()
                .first()
            )

    @classmethod
    def get_or_create_many(cls, session: Session, names: list[str]) -> list[Tag]:
        if not names:
            return []
        existing = {
            t.name: t
            for t in session.execute(select(cls).where(cls.name.in_(names))).scalars()
        }
        result: list[Tag] = []
        for name in names:
            tag = existing.get(name) or cls(name=name)
            if tag not in session:
                session.add(tag)
            result.append(tag)
        session.flush()
        return result
