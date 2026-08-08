from collections.abc import Iterator
from typing import cast

import jwt
import pytest
from fastapi.testclient import TestClient
from fsrs import Scheduler

from app_factory import create_app
from features.flashcard_scheduling import flashcard_scheduler_router

_USER_ID = "6f1c7d4e-0000-4000-8000-000000000001"
_GOOD_RATING = 3


class FakeCollection:
    def __init__(self, stored: dict[str, object] | None) -> None:
        super().__init__()
        self.stored: dict[str, object] | None = stored
        self.queries: list[dict[str, object]] = []

    def find_one(self, query: dict[str, object]) -> dict[str, object] | None:
        self.queries.append(query)

        return self.stored


class FakeDatabase:
    def __init__(self, collection: FakeCollection) -> None:
        super().__init__()
        self.collection: FakeCollection = collection

    def __getitem__(self, name: str) -> FakeCollection:
        return self.collection


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(create_app()) as test_client:
        yield test_client


def _use_stored_scheduler(
    monkeypatch: pytest.MonkeyPatch, stored: dict[str, object] | None
) -> FakeCollection:
    collection = FakeCollection(stored)
    monkeypatch.setattr(
        flashcard_scheduler_router, "db", FakeDatabase(collection)
    )

    return collection


def _authorization() -> dict[str, str]:
    token = jwt.encode({"user_id": _USER_ID}, "secret", algorithm="HS256")

    return {"Authorization": f"Bearer {token}"}


def test_schedule_flashcard_without_a_stored_scheduler(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    collection = _use_stored_scheduler(monkeypatch, None)

    response = client.post(
        "/schedule-flashcard",
        json={"card": None, "rating": _GOOD_RATING, "user_id": _USER_ID},
    )

    assert response.status_code == 200
    assert "due" in response.json()["new_card"]
    assert collection.queries == [{"user_id": _USER_ID}]


def test_schedule_flashcard_with_a_stored_scheduler(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    stored: dict[str, object] = dict(
        Scheduler(desired_retention=0.75).to_dict()
    )
    stored["_id"] = "mongo-id"
    collection = _use_stored_scheduler(monkeypatch, stored)

    response = client.post(
        "/schedule-flashcard",
        json={"card": None, "rating": _GOOD_RATING, "user_id": _USER_ID},
    )

    assert response.status_code == 200
    assert "review_log" in response.json()
    assert collection.queries == [{"user_id": _USER_ID}]


def test_ratings_times_requires_a_token(client: TestClient) -> None:
    response = client.post("/ratings-times", json={"card": None})

    assert response.status_code == 401


def test_ratings_times_returns_a_time_per_rating(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    _ = _use_stored_scheduler(monkeypatch, None)

    response = client.post(
        "/ratings-times", json={"card": None}, headers=_authorization()
    )

    assert response.status_code == 200
    ratings_times = cast("dict[str, int]", response.json())

    assert sorted(ratings_times) == ["1", "2", "3", "4"]


