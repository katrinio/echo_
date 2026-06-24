import re

_SPLIT_RE = re.compile(r"[,\s]+")


def slug_from_title(title: str) -> str:
    slug = title.strip().upper()
    slug = re.sub(r"[^A-Z0-9]+", "_", slug)
    slug = re.sub(r"_+", "_", slug)
    return slug.strip("_")


def slug_with_suffix(base_slug: str, suffix: int) -> str:
    if suffix <= 1:
        return base_slug
    return f"{base_slug}_{suffix}"


def parse_tags(raw_tags: str) -> list[str]:
    parts = _SPLIT_RE.split(raw_tags.strip())
    return sorted({part.strip().upper() for part in parts if part.strip()})
