import uuid
from collections.abc import Iterator
from typing import cast

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from app_factory import create_app
from shared.database import get_db
from shared.models import (
    Folder,
    Test,
    TestItem,
    TestItemReview,
    TestSession,
)
from tests.support import (
    OTHER_USER_ID,
    USER_ID,
    SessionProvider,
    authorization,
    in_memory_sessions,
)

_HOME_ID = uuid.UUID(USER_ID)
_QUESTION: dict[str, object] = {
    "question": "Which is a mammal?",
    "true_option": "whale",
    "false_options": ["shark", "trout"],
}


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    return in_memory_sessions()


@pytest.fixture
def client(sessions: sessionmaker[Session]) -> Iterator[TestClient]:
    app = create_app()
    app.dependency_overrides[get_db] = SessionProvider(sessions)

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def test_id(sessions: sessionmaker[Session]) -> str:
    with sessions() as session:
        folder = Folder(id=_HOME_ID, name="Home", user_id=_HOME_ID)
        session.add(folder)
        quiz = Test(folder_id=folder.id, name="Quiz")
        quiz.test_items.append(
            TestItem(content=_QUESTION, type="mult_choice")
        )
        session.add(quiz)
        session.commit()

        return str(quiz.id)


def test_fetching_items_opens_a_session(
    client: TestClient, test_id: str
) -> None:
    response = client.get(
        "/test-items", params={"test_id": test_id}, headers=authorization()
    )

    body = cast("dict[str, object]", response.json())

    assert body["total_items"] == 1
    assert body["test_session"]


def test_fetching_items_reuses_an_open_session(
    client: TestClient, test_id: str
) -> None:
    first = client.get(
        "/test-items", params={"test_id": test_id}, headers=authorization()
    )
    session_id = cast("dict[str, str]", first.json())["test_session"]

    second = client.get(
        "/test-items", params={"test_id": test_id}, headers=authorization()
    )

    assert cast("dict[str, str]", second.json())["test_session"] == session_id


def test_fetching_items_by_folder(
    client: TestClient, test_id: str
) -> None:
    assert test_id

    response = client.get(
        "/test-items",
        params={"folder_id": "home"},
        headers=authorization(),
    )

    assert cast("dict[str, object]", response.json())["total_items"] == 1


def test_fetching_items_needs_a_test_or_folder(client: TestClient) -> None:
    response = client.get("/test-items", headers=authorization())

    assert response.status_code == 404


def test_reviewing_an_item_records_the_answer(
    client: TestClient, sessions: sessionmaker[Session], test_id: str
) -> None:
    opened = client.get(
        "/test-items", params={"test_id": test_id}, headers=authorization()
    )
    session_id = cast("dict[str, str]", opened.json())["test_session"]

    with sessions() as session:
        item_id = session.query(TestItem).one().id

    response = client.post(
        "/review-test-item",
        json={
            "test_item_id": item_id,
            "test_session": session_id,
            "answers": [0],
        },
    )

    with sessions() as session:
        stored = session.query(TestItemReview).one()

    assert response.json() == {"msg": "Saved!"}
    assert stored.accuracy == 1


def test_reviewing_an_item_twice_updates_the_answer(
    client: TestClient, sessions: sessionmaker[Session], test_id: str
) -> None:
    opened = client.get(
        "/test-items", params={"test_id": test_id}, headers=authorization()
    )
    session_id = cast("dict[str, str]", opened.json())["test_session"]

    with sessions() as session:
        item_id = session.query(TestItem).one().id

    payload = {
        "test_item_id": item_id,
        "test_session": session_id,
        "answers": [0],
    }
    _ = client.post("/review-test-item", json=payload)
    _ = client.post("/review-test-item", json={**payload, "answers": [1]})

    with sessions() as session:
        stored = session.query(TestItemReview).one()

    assert stored.accuracy == 0


def test_previous_answers_come_back_with_the_items(
    client: TestClient, sessions: sessionmaker[Session], test_id: str
) -> None:
    opened = client.get(
        "/test-items", params={"test_id": test_id}, headers=authorization()
    )
    session_id = cast("dict[str, str]", opened.json())["test_session"]

    with sessions() as session:
        item_id = session.query(TestItem).one().id

    _ = client.post(
        "/review-test-item",
        json={
            "test_item_id": item_id,
            "test_session": session_id,
            "answers": [0],
        },
    )

    again = client.get(
        "/test-items",
        params={"test_id": test_id, "test_session": session_id},
        headers=authorization(),
    )
    items = cast(
        "dict[str, list[dict[str, object]]]", again.json()
    )["test_items"]

    assert items[0]["last_answers"] == [0]


def test_answers_from_another_session_are_not_returned(
    client: TestClient, sessions: sessionmaker[Session], test_id: str
) -> None:
    opened = client.get(
        "/test-items", params={"test_id": test_id}, headers=authorization()
    )
    session_id = cast("dict[str, str]", opened.json())["test_session"]

    with sessions() as session:
        item_id = session.query(TestItem).one().id

    _ = client.post(
        "/review-test-item",
        json={
            "test_item_id": item_id,
            "test_session": session_id,
            "answers": [0],
        },
    )
    other_session = uuid.uuid4()

    with sessions() as session:
        session.add(
            TestSession(
                id=other_session,
                origin_id=uuid.UUID(test_id),
                status="ongoing",
            )
        )
        session.commit()

    again = client.get(
        "/test-items",
        params={"test_id": test_id, "test_session": str(other_session)},
        headers=authorization(),
    )
    items = cast(
        "dict[str, list[dict[str, object]]]", again.json()
    )["test_items"]

    assert items[0]["last_answers"] is None


def test_an_answer_for_another_item_is_not_returned(
    client: TestClient, sessions: sessionmaker[Session], test_id: str
) -> None:
    opened = client.get(
        "/test-items", params={"test_id": test_id}, headers=authorization()
    )
    session_id = cast("dict[str, str]", opened.json())["test_session"]

    with sessions() as session:
        session.add(
            TestItemReview(
                test_session=uuid.UUID(session_id),
                test_item_id=999,
                accuracy=1,
                answers=[0],
            )
        )
        session.commit()

    again = client.get(
        "/test-items",
        params={"test_id": test_id, "test_session": session_id},
        headers=authorization(),
    )
    items = cast(
        "dict[str, list[dict[str, object]]]", again.json()
    )["test_items"]

    assert items[0]["last_answers"] is None


def test_a_finished_session_is_not_reused(
    client: TestClient, sessions: sessionmaker[Session], test_id: str
) -> None:
    with sessions() as session:
        session.add(
            TestSession(origin_id=uuid.UUID(test_id), status="done")
        )
        session.commit()

    response = client.get(
        "/test-items", params={"test_id": test_id}, headers=authorization()
    )
    opened = cast("dict[str, str]", response.json())["test_session"]

    with sessions() as session:
        statuses = {
            str(row.id): row.status
            for row in session.query(TestSession).all()
        }

    assert statuses[opened] == "ongoing"
    assert len(statuses) == 2


def test_a_session_for_another_origin_is_not_reused(
    client: TestClient, sessions: sessionmaker[Session], test_id: str
) -> None:
    with sessions() as session:
        session.add(TestSession(origin_id=uuid.uuid4(), status="ongoing"))
        session.commit()

    response = client.get(
        "/test-items", params={"test_id": test_id}, headers=authorization()
    )
    opened = cast("dict[str, str]", response.json())["test_session"]

    with sessions() as session:
        origins = {
            str(row.id): str(row.origin_id)
            for row in session.query(TestSession).all()
        }

    assert origins[opened] == test_id
    assert len(origins) == 2


def test_items_under_a_folder_i_do_not_own_are_hidden(
    client: TestClient, sessions: sessionmaker[Session], test_id: str
) -> None:
    assert test_id

    with sessions() as session:
        home = session.query(Folder).filter_by(id=_HOME_ID).one()
        home.user_id = uuid.UUID(OTHER_USER_ID)
        session.commit()

    response = client.get(
        "/test-items",
        params={"folder_id": "home"},
        headers=authorization(),
    )

    assert cast("dict[str, object]", response.json())["total_items"] == 0
