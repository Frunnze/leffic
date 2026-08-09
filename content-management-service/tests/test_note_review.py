import uuid
from collections.abc import Iterator
from typing import cast

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from app_factory import create_app
from shared.database import get_db
from shared.models import Folder, Note
from tests.support import (
    USER_ID,
    SessionProvider,
    authorization,
    in_memory_sessions,
)

_HOME_ID = uuid.UUID(USER_ID)


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    return in_memory_sessions()


@pytest.fixture
def client(sessions: sessionmaker[Session]) -> Iterator[TestClient]:
    app = create_app()
    app.dependency_overrides[get_db] = SessionProvider(sessions)

    with TestClient(app) as test_client:
        yield test_client


def _stored_note(sessions: sessionmaker[Session]) -> str:
    with sessions() as session:
        folder = Folder(id=_HOME_ID, name="Home", user_id=_HOME_ID)
        session.add(folder)
        note = Note(
            folder_id=folder.id, name="N", content="body", type="general"
        )
        session.add(note)
        session.commit()

        return str(note.id)


def test_reading_a_note_leaves_it_unread(
    client: TestClient, sessions: sessionmaker[Session]
) -> None:
    note_id = _stored_note(sessions)

    first = client.get("/note", params={"note_id": note_id})

    with sessions() as session:
        assert not session.query(Note).one().read

    assert cast("dict[str, str]", first.json())["content"] == "body"


def test_reviewing_a_note_marks_it_read(
    client: TestClient, sessions: sessionmaker[Session]
) -> None:
    note_id = _stored_note(sessions)

    response = client.post(
        "/review-note",
        json={"note_id": note_id},
        headers=authorization(str(_HOME_ID)),
    )

    assert response.status_code == 200

    with sessions() as session:
        assert session.query(Note).one().read


def test_reviewing_a_note_twice_keeps_it_read(
    client: TestClient, sessions: sessionmaker[Session]
) -> None:
    note_id = _stored_note(sessions)
    payload = {"note_id": note_id}

    _ = client.post(
        "/review-note", json=payload, headers=authorization(str(_HOME_ID))
    )
    second = client.post(
        "/review-note", json=payload, headers=authorization(str(_HOME_ID))
    )

    assert second.status_code == 200

    with sessions() as session:
        assert session.query(Note).one().read


def test_reviewing_an_unknown_note_is_not_found(client: TestClient) -> None:
    response = client.post(
        "/review-note",
        json={"note_id": str(uuid.uuid4())},
        headers=authorization(str(_HOME_ID)),
    )

    assert response.status_code == 404


def test_reviewing_a_note_of_another_user_is_rejected(
    client: TestClient, sessions: sessionmaker[Session]
) -> None:
    note_id = _stored_note(sessions)

    response = client.post(
        "/review-note",
        json={"note_id": note_id},
        headers=authorization(str(uuid.uuid4())),
    )

    assert response.status_code == 404

    with sessions() as session:
        assert not session.query(Note).one().read




def test_reading_a_note_reports_its_read_state(
    client: TestClient, sessions: sessionmaker[Session]
) -> None:
    note_id = _stored_note(sessions)

    before = client.get("/note", params={"note_id": note_id})

    assert cast("dict[str, object]", before.json())["read"] is False

    _ = client.post(
        "/review-note",
        json={"note_id": note_id},
        headers=authorization(str(_HOME_ID)),
    )
    after = client.get("/note", params={"note_id": note_id})

    assert cast("dict[str, object]", after.json())["read"] is True
