from src.features.auth.security import SESSION_COOKIE_NAME


class TestAuthMiddleware:
    def test_login_page_is_public(self, client):
        response = client.get("/login", follow_redirects=False)
        assert response.status_code == 200

    def test_logout_is_public(self, client):
        response = client.get("/logout", follow_redirects=False)
        assert response.status_code == 303

    def test_static_files_are_public(self, client):
        # Статика не блокируется миддлварой, даже без авторизации.
        response = client.get("/static/css/base.css", follow_redirects=False)
        assert response.status_code != 303

    def test_protected_route_redirects_to_login(self, client):
        client.cookies.clear()
        response = client.get("/", follow_redirects=False)
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
