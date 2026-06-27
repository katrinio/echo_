from pathlib import Path
import importlib
import sys

import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from starlette.testclient import TestClient

from src.app import app
from src.database import Base
from src.config import settings

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Импортируем модели чтобы они зарегистрировались в Base.metadata до create_all.
importlib.import_module("src.orm.milestone")
importlib.import_module("src.orm.tag")


@pytest.fixture(scope="session", autouse=True)
def configure_test_settings():
    """Минимальные настройки для тестов."""
    settings.session_secret_key = "test-secret-key"
    settings.echo_password = "test-password"


@pytest.fixture(scope="session")
def db_engine():
    """In-memory SQLite на всю сессию тестов."""
    # StaticPool — одно соединение для всех сессий, иначе каждый Session()
    # получает пустую in-memory БД и не видит созданные таблицы.
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture(scope="session")
def client(db_engine, configure_test_settings):
    """TestClient с подменённым движком БД."""
    import src.database as db_module
    import src.orm.milestone as milestone_module
    import src.orm.tag as tag_module

    db_module.engine = db_engine
    milestone_module.engine = db_engine
    tag_module.engine = db_engine

    with TestClient(app, raise_server_exceptions=True) as c:
        yield c


@pytest.fixture
def auth_client(client):
    """TestClient с валидной сессионной cookie."""
    from src.features.auth.security import create_session_token, SESSION_COOKIE_NAME
    client.cookies.set(SESSION_COOKIE_NAME, create_session_token())
    yield client
    client.cookies.clear()
