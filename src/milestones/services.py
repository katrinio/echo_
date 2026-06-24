from collections import OrderedDict
from collections.abc import Sequence

from src.orm.milestone import Milestone


def group_by_day(milestones: Sequence[Milestone]) -> OrderedDict[str, list[Milestone]]:
    grouped: dict[str, list[Milestone]] = {}
    for milestone in milestones:
        day = str(milestone.happened_at)
        grouped.setdefault(day, []).append(milestone)
    return OrderedDict(sorted(grouped.items(), reverse=True))
