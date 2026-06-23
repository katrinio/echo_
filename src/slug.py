from __future__ import annotations

import re


def slug_from_title(title: str) -> str:
    slug = title.strip().upper()
    slug = re.sub(r"[^A-Z0-9]+", "_", slug)
    slug = re.sub(r"_+", "_", slug)
    return slug.strip("_")


def slug_with_suffix(base_slug: str, suffix: int) -> str:
    if suffix <= 1:
        return base_slug
    return f"{base_slug}_{suffix}"
