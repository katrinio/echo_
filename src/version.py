"""Asset versioning for cache busting on deployment."""

import os
import subprocess
from pathlib import Path


class AssetVersionError(RuntimeError):
    """Raised when a production deployment does not provide an asset version."""


def get_version_string() -> str:
    """Return a stable build version used by every versioned PWA resource."""
    version = os.environ.get("ECHO_VERSION", "").strip()
    if version and version != "local":
        return version

    try:
        repo_root = Path(__file__).resolve().parents[1]
        if (repo_root / ".git").exists():
            output = subprocess.check_output(
                ["git", "rev-parse", "--short", "HEAD"],
                cwd=repo_root,
                stderr=subprocess.DEVNULL,
                text=True,
            ).strip()
            if output:
                return output
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    if _is_production_environment():
        raise AssetVersionError(
            "ECHO_VERSION must be set to a non-local commit SHA, git tag, or build id in production"
        )

    return version or "local"


def _is_production_environment() -> bool:
    value = (
        (os.environ.get("ECHO_ENV") or os.environ.get("APP_ENV") or os.environ.get("ENVIRONMENT") or "")
        .strip()
        .lower()
    )
    return value in {"production", "prod"}
