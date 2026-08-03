import subprocess

import pytest
from starlette.testclient import TestClient

import src.version as version_module
from src.app import app
from src.features.auth.security import SESSION_COOKIE_NAME


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
        response = client.get("/manifest.webmanifest", follow_redirects=False)

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("application/manifest+json")
        assert response.headers["cache-control"] == "no-cache"

        manifest = response.json()
        icon_urls = [icon["src"] for icon in manifest["icons"]]
        expected_version = version_module.get_version_string()
        versions = {url.split("?v=", 1)[1] for url in icon_urls}
        assert versions == {expected_version}
        assert icon_urls == [
            f"/static/icons/pwa-icon-192x192.png?v={expected_version}",
            f"/static/icons/pwa-icon-256x256.png?v={expected_version}",
            f"/static/icons/pwa-icon-384x384.png?v={expected_version}",
            f"/static/icons/pwa-icon-512x512.png?v={expected_version}",
            f"/static/icons/pwa-maskable-192x192.png?v={expected_version}",
            f"/static/icons/pwa-maskable-512x512.png?v={expected_version}",
        ]
        assert {icon["purpose"] for icon in manifest["icons"]} >= {"any", "maskable"}

    def test_versioned_pwa_icon_keeps_immutable_cache_header(self, client):
        response = client.get("/static/icons/pwa-icon-192x192.png", follow_redirects=False)
        assert response.status_code == 200
        assert response.headers["cache-control"] == "no-cache"

        response = client.get(
            f"/static/icons/pwa-icon-192x192.png?v={version_module.get_version_string()}",
            follow_redirects=False,
        )

        assert response.status_code == 200
        assert response.headers["cache-control"] == "public, max-age=31536000, immutable"

    def test_manifest_icon_urls_include_root_path(self):
        with TestClient(app, root_path="/echo") as client:
            response = client.get("/manifest.webmanifest", follow_redirects=False)

        assert response.status_code == 200
        icon_urls = [icon["src"] for icon in response.json()["icons"]]
        assert all(url.startswith("/echo/static/icons/") for url in icon_urls)

    def test_manifest_uses_one_build_version_for_every_icon(self, client, monkeypatch):
        monkeypatch.setenv("ECHO_VERSION", "deploy-123")

        response = client.get("/manifest.webmanifest", follow_redirects=False)

        versions = {icon["src"].split("?v=", 1)[1] for icon in response.json()["icons"]}
        assert versions == {"deploy-123"}

    def test_html_pwa_resources_use_build_version(self, auth_client, monkeypatch):
        monkeypatch.setenv("ECHO_VERSION", "deploy-456")

        response = auth_client.get("/", follow_redirects=False)

        assert response.status_code == 200
        assert "/manifest.webmanifest?v=deploy-456" in response.text
        assert "/static/icons/favicon.ico?v=deploy-456" in response.text
        assert "/static/icons/apple-touch-icon-180x180.png?v=deploy-456" in response.text
        assert "/static/icons/safari-pinned-tab.svg?v=deploy-456" in response.text
        assert "/sw.js?v=" not in response.text

    def test_service_worker_is_public_and_not_cached(self, client):
        response = client.get("/sw.js", follow_redirects=False)

        assert response.status_code == 200
        assert response.headers["cache-control"] == "no-cache"
        assert "serviceWorker" not in response.text

    def test_production_requires_non_local_asset_version(self, monkeypatch):
        monkeypatch.delenv("ECHO_VERSION", raising=False)
        monkeypatch.setattr(version_module, "_is_production_environment", lambda: True)
        monkeypatch.setattr(
            version_module.subprocess,
            "check_output",
            lambda *args, **kwargs: (_ for _ in ()).throw(subprocess.CalledProcessError(1, "git")),
        )

        with pytest.raises(version_module.AssetVersionError, match="ECHO_VERSION must be set"):
            version_module.get_version_string()

        monkeypatch.setenv("ECHO_VERSION", "local")
        with pytest.raises(version_module.AssetVersionError, match="ECHO_VERSION must be set"):
            version_module.get_version_string()

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
