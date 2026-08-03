from pathlib import Path

from fastapi import Request
from fastapi.templating import Jinja2Templates

from src.config import settings
from src.version import get_version_string

_TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=_TEMPLATES_DIR)


def _asset_version(rel_path: str) -> str:
    return get_version_string()


def _static_url(request: Request, rel_path: str) -> str:
    version = _asset_version(rel_path)
    root_path = request.scope.get("root_path", "")
    path = request.app.url_path_for("static", path=rel_path)
    return f"{root_path}{path}?v={version}"


static_url = _static_url

templates.env.globals["asset_version"] = _asset_version
templates.env.globals["static_url"] = static_url
templates.env.globals["settings"] = settings
