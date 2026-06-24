from datetime import date

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.milestones.helpers import parse_tags
from src.database import Base
from src.orm.milestone import Milestone
from src.orm.tag import Tag


def _setup_engine(tmp_path, monkeypatch):
    engine = create_engine(f"sqlite:///{tmp_path / 'test.db'}")
    monkeypatch.setattr("src.orm.milestone.engine", engine)
    monkeypatch.setattr("src.orm.tag.engine", engine)
    Base.metadata.create_all(engine)
    return engine


def test_parse_tags_normalizes_duplicates_and_order():
    assert parse_tags("vpn, infra friends") == ["FRIENDS", "INFRA", "VPN"]


def test_parse_tags_handles_repeated_values():
    assert parse_tags("vpn vpn infra") == ["INFRA", "VPN"]


def test_parse_tags_handles_empty_string():
    assert parse_tags("") == []


def test_create_milestone_creates_tags_and_relations(tmp_path, monkeypatch):
    engine = _setup_engine(tmp_path, monkeypatch)

    milestone = Milestone.create_with_title(
        title="VPN for friends",
        happened_at=date(2026, 6, 22),
        description="",
        tags=parse_tags("vpn infra friends"),
    )

    assert [tag.name for tag in milestone.tags] == ["FRIENDS", "INFRA", "VPN"]
    with Session(engine) as session:
        assert [tag.name for tag in session.query(Tag).order_by(Tag.name).all()] == [
            "FRIENDS",
            "INFRA",
            "VPN",
        ]


def test_duplicate_tags_are_reused(tmp_path, monkeypatch):
    engine = _setup_engine(tmp_path, monkeypatch)

    first = Milestone.create_with_title(
        title="VPN for friends",
        happened_at=date(2026, 6, 22),
        tags=parse_tags("vpn infra"),
    )
    second = Milestone.create_with_title(
        title="Infra notes",
        happened_at=date(2026, 6, 21),
        tags=parse_tags("infra"),
    )

    assert [tag.name for tag in first.tags] == ["INFRA", "VPN"]
    assert [tag.name for tag in second.tags] == ["INFRA"]
    with Session(engine) as session:
        assert session.query(Tag).count() == 2


def test_updating_milestone_replaces_tag_relations(tmp_path, monkeypatch):
    engine = _setup_engine(tmp_path, monkeypatch)

    milestone = Milestone.create_with_title(
        title="VPN for friends",
        happened_at=date(2026, 6, 22),
        tags=parse_tags("vpn infra friends"),
    )

    updated = Milestone.update_by_slug(
        milestone.slug,
        title="VPN for friends",
        happened_at=date(2026, 6, 22),
        description="",
        tags=parse_tags("infra"),
    )

    assert [tag.name for tag in updated.tags] == ["INFRA"]
    with Session(engine) as session:
        assert [tag.name for tag in session.query(Tag).order_by(Tag.name).all()] == [
            "FRIENDS",
            "INFRA",
            "VPN",
        ]


def test_tag_page_uses_all_milestones_for_tag(tmp_path, monkeypatch):
    _setup_engine(tmp_path, monkeypatch)

    first = Milestone.create_with_title(
        title="VPN for friends",
        happened_at=date(2026, 6, 22),
        tags=parse_tags("vpn infra"),
    )
    second = Milestone.create_with_title(
        title="Another VPN note",
        happened_at=date(2026, 6, 21),
        tags=parse_tags("vpn"),
    )
    Milestone.create_with_title(
        title="Unrelated",
        happened_at=date(2026, 6, 20),
        tags=parse_tags("infra"),
    )

    tag = Tag.get_by_name("VPN")
    assert tag is not None
    assert [m.slug for m in tag.milestones] == [first.slug, second.slug]
