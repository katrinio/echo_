from datetime import date

import pytest

from src.orm.milestone import Milestone


@pytest.fixture
def milestone(db_engine):
    """Создаёт тестовую веху в БД."""
    import src.orm.milestone as m
    m.engine = db_engine
    milestone = Milestone.create_with_title(
        title="Test Milestone",
        happened_at=date(2026, 1, 1),
        description="Test description",
        tags=["WORK", "TEST"],
    )
    yield milestone


# ===== Auth routes =====

class TestLoginRoute:
    def test_get_login_page(self, client):
        response = client.get("/login")
        assert response.status_code == 200

    def test_post_wrong_password_returns_401(self, client):
        response = client.post("/login", data={"password": "wrong", "next": "/"})
        assert response.status_code == 401

    def test_post_correct_password_redirects(self, client):
        response = client.post(
            "/login",
            data={"password": "test-password", "next": "/"},
            follow_redirects=False,
        )
        assert response.status_code == 303
        assert response.headers["location"] == "/"

    def test_post_correct_password_sets_cookie(self, client):
        response = client.post(
            "/login",
            data={"password": "test-password", "next": "/"},
            follow_redirects=False,
        )
        assert "echo_session" in response.headers.get("set-cookie", "")

    def test_post_redirects_to_next_url(self, client):
        response = client.post(
            "/login",
            data={"password": "test-password", "next": "/milestones/test"},
            follow_redirects=False,
        )
        assert response.headers["location"] == "/milestones/test"

    def test_get_logout_clears_cookie_and_redirects(self, auth_client):
        response = auth_client.get("/logout", follow_redirects=False)
        assert response.status_code == 303
        assert response.headers["location"] == "/login"


# ===== Milestone routes =====

class TestMilestoneRoutes:
    def test_index_returns_200(self, auth_client):
        response = auth_client.get("/")
        assert response.status_code == 200

    def test_new_page_returns_200(self, auth_client):
        response = auth_client.get("/new")
        assert response.status_code == 200

    def test_create_milestone_redirects(self, auth_client):
        response = auth_client.post(
            "/new",
            data={
                "title": "My Route Test",
                "happened_at": "2026-01-15",
                "description": "",
                "tags": "",
            },
            follow_redirects=False,
        )
        assert response.status_code == 303
        assert response.headers["location"] == "/"

    def test_create_milestone_invalid_title_returns_422(self, auth_client):
        response = auth_client.post(
            "/new",
            data={
                "title": "Кириллица запрещена",
                "happened_at": "2026-01-15",
                "description": "",
                "tags": "",
            },
        )
        assert response.status_code == 422

    def test_detail_page_returns_200(self, auth_client, milestone):
        response = auth_client.get(f"/milestones/{milestone.slug}")
        assert response.status_code == 200

    def test_edit_page_returns_200(self, auth_client, milestone):
        response = auth_client.get(f"/milestones/{milestone.slug}/edit")
        assert response.status_code == 200

    def test_update_milestone_redirects(self, auth_client, milestone):
        response = auth_client.post(
            f"/milestones/{milestone.slug}/edit",
            data={
                "title": "Updated Title",
                "happened_at": "2026-01-20",
                "description": "Updated",
                "tags": "WORK",
            },
            follow_redirects=False,
        )
        assert response.status_code == 303


# ===== Tag routes =====

class TestTagRoutes:
    def test_tags_list_returns_200(self, auth_client):
        response = auth_client.get("/tags")
        assert response.status_code == 200

    def test_tag_page_returns_200(self, auth_client, milestone):
        response = auth_client.get("/tags/WORK")
        assert response.status_code == 200

    def test_unknown_tag_returns_404(self, auth_client):
        response = auth_client.get("/tags/NONEXISTENT_TAG_XYZ")
        assert response.status_code == 404


# ===== Terminal routes =====

class TestTerminalRoutes:
    def test_help_page_returns_200(self, auth_client):
        response = auth_client.get("/help")
        assert response.status_code == 200

    def test_random_redirects_when_no_milestones(self, auth_client):
        response = auth_client.get("/random", follow_redirects=False)
        # 200 (plain text) если нет вех, иначе 303
        assert response.status_code in (200, 303)

    def test_search_returns_200(self, auth_client):
        response = auth_client.get("/search?q=test")
        assert response.status_code == 200

    def test_tree_returns_200(self, auth_client):
        response = auth_client.get("/tree")
        assert response.status_code == 200

    def test_terminal_commands_returns_json(self, auth_client):
        response = auth_client.get("/terminal/commands")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert any(cmd["command"] == "help" for cmd in data)
        assert any(cmd["command"] == "tree" for cmd in data)
