from collections.abc import Iterator
from typing import cast

import pytest
from fastapi.testclient import TestClient

from app_factory import create_app
from tests.support import authorization

_UNAUTHORIZED = 401


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(create_app()) as test_client:
        yield test_client


def _intervals(
    client: TestClient, payload: dict[str, object]
) -> dict[str, int]:
    response = client.post(
        "/rating-intervals", json=payload, headers=authorization()
    )

    return cast("dict[str, int]", response.json())


def test_a_new_card_gets_an_interval_for_every_rating(
    client: TestClient,
) -> None:
    intervals = _intervals(client, {})

    assert sorted(intervals) == ["1", "2", "3", "4"]


def test_easier_ratings_wait_longer(client: TestClient) -> None:
    intervals = _intervals(client, {})

    assert intervals["4"] > intervals["1"]
    assert intervals["3"] > intervals["1"]


def test_the_intervals_are_never_negative(client: TestClient) -> None:
    intervals = _intervals(client, {})

    assert min(intervals.values()) >= 0


def test_rating_intervals_need_a_token(client: TestClient) -> None:
    response = client.post("/rating-intervals", json={})

    assert response.status_code == _UNAUTHORIZED
