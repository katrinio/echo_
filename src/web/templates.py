from pathlib import Path

from fastapi import Request
from fastapi.templating import Jinja2Templates

from src.config import settings

_TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=_TEMPLATES_DIR)


def _asset_version(rel_path: str) -> int:
    return int((_TEMPLATES_DIR.parent / "static" / rel_path).stat().st_mtime)


def _static_url(request: Request, rel_path: str) -> str:
    version = _asset_version(rel_path)
    return f"{request.url_for('static', path=rel_path)}?v={version}"


templates.env.globals["asset_version"] = _asset_version
templates.env.globals["static_url"] = _static_url
templates.env.globals["settings"] = settings
