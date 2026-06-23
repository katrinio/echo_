from __future__ import annotations

from pathlib import Path


TEMPLATE_DIR = Path("src/templates")
REQUIRED_EXTENDS = '{% extends "base.html" %}'


def main() -> int:
    errors: list[str] = []
    for path in sorted(TEMPLATE_DIR.glob("*.html")):
        text = path.read_text(encoding="utf-8")
        if path.name != "base.html" and REQUIRED_EXTENDS not in text:
            errors.append(f"{path}: missing base template extension")
        if text.count("{% block ") != text.count("{% endblock %}"):
            errors.append(f"{path}: unmatched block tags")
        if text.count("{{") != text.count("}}"):
            errors.append(f"{path}: unmatched variable tags")
    if errors:
        for error in errors:
            print(error)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
