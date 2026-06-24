from src.orm.milestone import Milestone
from src.orm.tag import Tag


def get_milestones_for_tag(tag_name: str) -> list[Milestone]:
    tag = Tag.get_by_name(tag_name.upper())
    if tag is None:
        return []
    return list(tag.milestones)
