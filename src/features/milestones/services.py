from collections import OrderedDict
from collections.abc import Sequence

from src.orm.milestone import Milestone


def group_by_day(milestones: Sequence[Milestone]) -> OrderedDict[str, list[Milestone]]:
    grouped: dict[str, list[Milestone]] = {}
    for milestone in milestones:
        day = str(milestone.happened_at)
        grouped.setdefault(day, []).append(milestone)
    return OrderedDict(sorted(grouped.items(), reverse=True))


def group_by_year_and_month(
    milestones: Sequence[Milestone],
) -> OrderedDict[int, OrderedDict[str, list[Milestone]]]:
    months = {
        1: "Jan",
        2: "Feb",
        3: "Mar",
        4: "Apr",
        5: "May",
        6: "Jun",
        7: "Jul",
        8: "Aug",
        9: "Sep",
        10: "Oct",
        11: "Nov",
        12: "Dec",
    }

    grouped: dict[int, dict[int, list[Milestone]]] = {}
    for milestone in milestones:
        year = milestone.happened_at.year
        month = milestone.happened_at.month
        grouped.setdefault(year, {}).setdefault(month, []).append(milestone)

    ordered: OrderedDict[int, OrderedDict[str, list[Milestone]]] = OrderedDict()
    for year in sorted(grouped, reverse=True):
        month_groups = grouped[year]
        ordered[year] = OrderedDict(
            (
                months[month],
                sorted(month_groups[month], key=lambda item: item.happened_at),
            )
            for month in sorted(month_groups, reverse=True)
        )
    return ordered
