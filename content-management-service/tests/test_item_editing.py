import uuid
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from app_factory import create_app
from shared.database import get_db
from shared.models import FlashcardDeck, Folder, Test, TestItem
from tests.support import (
    OTHER_USER_ID,
    USER_ID,
    SessionProvider,
    authorization,
    in_memory_sessions,
)

_NOT_FOUND = 404
_OK = 200

HOME_ID = uuid.UUID(USER_ID)
_OTHER_HOME_ID = uuid.UUID(OTHER_USER_ID)


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    return in_memory_sessions()


@pytest.fixture
def client(sessions: sessionmaker[Session]) -> Iterator[TestClient]:
    app = create_app()
    app.dependency_overrides[get_db] = SessionProvider(sessions)

    with TestClient(app) as test_client:
        yield test_client


def home_folder(session: Session, user_id: uuid.UUID = HOME_ID) -> Folder:
    folder = Folder(id=user_id, name="Home", user_id=user_id)
    session.add(folder)
    session.commit()

    return folder


def deck(session: Session, name: str = "Deck") -> FlashcardDeck:
    created = FlashcardDeck(name=name, folder_id=HOME_ID)
    session.add(created)
    session.commit()

    return created


def test_updating_a_test_item_replaces_its_content(
    client: TestClient, sessions: sessionmaker[Session]
) -> None:
    with sessions() as session:
        _ = home_folder(session)
        test_unit = Test(name="Test", folder_id=HOME_ID)
        session.add(test_unit)
        session.commit()
        item = TestItem(
            test_id=test_unit.id,
            type="multiple_choice",
            content={"question": "Old?", "answers": ["a"]},
        )
        session.add(item)
        session.commit()
        item_id = item.id

    new_content = {"question": "New?", "answers": ["b", "c"], "correct": 0}
    response = client.patch(
        "/update-test-item",
        json={"test_item_id": item_id, "content": new_content},
        headers=authorization(),
    )

    assert response.status_code == _OK

    with sessions() as session:
        updated = session.query(TestItem).filter_by(id=item_id).one()

        assert updated.content == new_content


def test_updating_a_missing_test_item_is_not_found(
    client: TestClient, sessions: sessionmaker[Session]
) -> None:
    with sessions() as session:
        _ = home_folder(session)

    response = client.patch(
        "/update-test-item",
        json={"test_item_id": 4242, "content": {"question": "New?"}},
        headers=authorization(),
    )

    assert response.status_code == _NOT_FOUND
