import uuid
from pathlib import Path

from alembic.command import downgrade, upgrade
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, inspect, text

from tests.migration_support import INITIAL_REVISION, alembic_config
from tests.session_ownership_support import ONGOING

_BASE_COLUMNS = {"id", "origin_id", "status", "created_at"}
_SEED_SESSION = text("""
    INSERT INTO test_sessions (id, origin_id, status)
    VALUES (:id, :origin, :status)
""")
_SEED_REVIEW = text("""
    INSERT INTO test_item_reviews
    (test_session, test_item_id, accuracy, answers)
    VALUES (:session, 1, 1.0, '[]')
""")
_COUNT_SESSIONS = text("SELECT COUNT(*) FROM test_sessions")
_COUNT_REVIEWS = text("SELECT COUNT(*) FROM test_item_reviews")


def _session_columns(database_url: str) -> dict[str, object]:
    engine = create_engine(database_url)
    columns = inspect(engine).get_columns("test_sessions")

    return {column["name"]: column["nullable"] for column in columns}


def test_the_new_revision_is_the_single_head() -> None:
    scripts = ScriptDirectory.from_config(alembic_config("sqlite://"))
    heads = scripts.get_heads()
    head = scripts.get_revision(heads[0])

    assert len(heads) == 1
    assert head.down_revision == INITIAL_REVISION


def test_upgrade_clears_reviews_then_sessions(tmp_path: Path) -> None:
    database_url = f"sqlite:///{tmp_path / 'cleared.db'}"
    config = alembic_config(database_url)
    upgrade(config, INITIAL_REVISION)
    engine = create_engine(database_url)

    with engine.begin() as connection:
        session_id = str(uuid.uuid4())
        _ = connection.execute(
            _SEED_SESSION,
            {
                "id": session_id,
                "origin": str(uuid.uuid4()),
                "status": ONGOING,
            },
        )
        _ = connection.execute(_SEED_REVIEW, {"session": session_id})

    upgrade(config, "head")

    with engine.connect() as connection:
        remaining_reviews = connection.execute(_COUNT_REVIEWS).scalar()
        remaining_sessions = connection.execute(_COUNT_SESSIONS).scalar()

    assert remaining_reviews == 0
    assert remaining_sessions == 0


def test_upgrade_adds_a_non_nullable_user_id(tmp_path: Path) -> None:
    database_url = f"sqlite:///{tmp_path / 'upgraded.db'}"
    upgrade(alembic_config(database_url), "head")
    columns = _session_columns(database_url)

    assert "user_id" in columns
    assert columns["user_id"] is False


def test_downgrade_drops_user_id(tmp_path: Path) -> None:
    database_url = f"sqlite:///{tmp_path / 'reverted.db'}"
    config = alembic_config(database_url)
    upgrade(config, "head")
    upgraded = _session_columns(database_url)
    downgrade(config, INITIAL_REVISION)
    reverted = _session_columns(database_url)

    assert "user_id" in upgraded
    assert "user_id" not in reverted
    assert set(reverted) == _BASE_COLUMNS
