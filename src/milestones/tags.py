import re

_SPLIT_RE = re.compile(r"[,\s]+")


def parse_tags(raw_tags: str) -> list[str]:
    parts = _SPLIT_RE.split(raw_tags.strip())
    return sorted({part.strip().upper() for part in parts if part.strip()})
