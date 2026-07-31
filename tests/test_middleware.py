from pathlib import Path
import os

from starlette.testclient import TestClient

from src.app import app
from src.features.auth.security import SESSION_COOKIE_NAME

STATIC_DIR = Path(__file__).resolve().parents[1] / "src" / "static"


class TestAuthMiddleware:
    def test_login_page_is_public(self, client):
        response = client.get("/login", follow_redirects=False)
        assert response.status_code == 200

    def test_logout_requires_auth(self, client):
        client.cookies.clear()
        response = client.get("/logout", follow_redirects=False)
        assert response.status_code == 303
        assert "/login" in response.headers["location"]

    def test_health_is_public(self, client):
        response = client.get("/health", follow_redirects=False)
        assert response.status_code == 200
        assert "I am fine, thanks." in response.text

    def test_static_files_are_public(self, client):
        # Статика не блокируется миддлварой, даже без авторизации.
        response = client.get("/static/css/base.css", follow_redirects=False)
        assert response.status_code != 303

    def test_manifest_has_no_cache_header_and_versioned_icons(self, client):
        response = client.get("/static/site.webmanifest", follow_redirects=False)

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("application/manifest+json")
        assert response.headers["cache-control"] == "no-cache"

        manifest = response.json()
        icon_urls = [icon["src"] for icon in manifest["icons"]]
        expected_versions = {
            size: int((STATIC_DIR / "icons" / f"pwa-icon-{size}x{size}.png").stat().st_mtime)
            for size in (192, 256, 384, 512)
        }
        assert icon_urls == [
            f"/static/icons/pwa-icon-192x192.png?v={expected_versions[192]}",
            f"/static/icons/pwa-icon-256x256.png?v={expected_versions[256]}",
            f"/static/icons/pwa-icon-384x384.png?v={expected_versions[384]}",
            f"/static/icons/pwa-icon-512x512.png?v={expected_versions[512]}",
        ]

    def test_pwa_icon_keeps_immutable_cache_header(self, client):
        response = client.get("/static/icons/pwa-icon-192x192.png", follow_redirects=False)

        assert response.status_code == 200
        assert response.headers["cache-control"] == "public, max-age=31536000, immutable"

    def test_manifest_icon_urls_include_root_path(self):
        with TestClient(app, root_path="/echo") as client:
            response = client.get("/static/site.webmanifest", follow_redirects=False)

        assert response.status_code == 200
        icon_urls = [icon["src"] for icon in response.json()["icons"]]
        assert all(url.startswith("/echo/static/icons/") for url in icon_urls)

    def test_manifest_icon_url_changes_when_icon_mtime_changes(self, client):
        icon_path = STATIC_DIR / "icons" / "pwa-icon-192x192.png"
        original_stat = icon_path.stat()

        try:
            initial_response = client.get("/static/site.webmanifest", follow_redirects=False)
            os.utime(icon_path, (original_stat.st_atime, original_stat.st_mtime + 2))
            updated_response = client.get("/static/site.webmanifest", follow_redirects=False)
        finally:
            os.utime(icon_path, (original_stat.st_atime, original_stat.st_mtime))

        initial_url = initial_response.json()["icons"][0]["src"]
        updated_url = updated_response.json()["icons"][0]["src"]
        assert initial_url != updated_url

    def test_protected_route_redirects_to_login(self, client):
        client.cookies.clear()
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 303
        assert "/login" in response.headers["location"]

    def test_search_redirects_to_login_without_cookie(self, client):
        client.cookies.clear()
        response = client.get("/search?q=test", follow_redirects=False)
        assert response.status_code == 303
        assert "/login" in response.headers["location"]

    def test_detail_redirects_to_login_without_cookie(self, client):
        client.cookies.clear()
        response = client.get("/milestones/some-slug", follow_redirects=False)
        assert response.status_code == 303
        assert "/login" in response.headers["location"]

    def test_create_redirects_to_login_without_cookie(self, client):
        client.cookies.clear()
        response = client.post("/new", data={}, follow_redirects=False)
        assert response.status_code == 303
        assert "/login" in response.headers["location"]

    def test_edit_redirects_to_login_without_cookie(self, client):
        client.cookies.clear()
        response = client.post("/milestones/some-slug/edit", data={}, follow_redirects=False)
        assert response.status_code == 303
        assert "/login" in response.headers["location"]

    def test_redirect_contains_next_param(self, client):
        client.cookies.clear()
        response = client.get("/milestones/some-slug", follow_redirects=False)
        assert "next=" in response.headers["location"]

    def test_authenticated_request_passes_through(self, auth_client):
        response = auth_client.get("/", follow_redirects=False)
        assert response.status_code == 200

    def test_expired_cookie_redirects_to_login(self, client):
        client.cookies.set(SESSION_COOKIE_NAME, "invalid-token")
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 303
        client.cookies.clear()


class TestSmokeCoverage:
    def test_login_page_responds(self, client):
        response = client.get("/login", follow_redirects=False)
        assert response.status_code == 200

    def test_root_redirects_without_auth(self, client):
        client.cookies.clear()
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 303
        assert "/login" in response.headers["location"]
