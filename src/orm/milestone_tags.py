from sqlalchemy import Column, ForeignKey, Integer, Table

from src.database import Base

milestone_tags = Table(
    "milestone_tags",
    Base.metadata,
    Column("milestone_id", Integer, ForeignKey("milestones.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)
