from collections.abc import Callable
from typing import cast

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from features.study_units import assessment_router
from features.study_units.formatting import evaluate_accuracy
from features.study_units.study_unit_access import owned_test_item
from shared.models import TestItem, TestItemReview
from tests.study_unit_access_support import (
    ABSENT_ROW_ID,
    MISSING_TEST_ITEM_DETAIL,
    NOT_FOUND,
    OK,
    StudyUnitWorld,
    refusing_item_lookup,
    review_payload,
)
from tests.support import authorization

_SessionGet = Callable[[Session, object, object], object]
_CHOSEN_OPTION: list[object] = [0]
_OTHER_OPTION: list[object] = [1]


class _CountingItemLookup:
    def __init__(self) -> None:
        self.calls: list[tuple[str, int]] = []

    def __call__(
        self, db: Session, user_id: str, test_item_id: int
    ) -> TestItem:
        self.calls.append((user_id, test_item_id))

        return owned_test_item(db, user_id, test_item_id)


class _RecordingGet:
    def __init__(self, original: _SessionGet) -> None:
        self.loaded_entities: list[object] = []
        self._original: _SessionGet = original

    def __call__(
        self, session: Session, entity: object, ident: object
    ) -> object:
        self.loaded_entities.append(entity)

        return self._original(session, entity, ident)


def _posted_review(
    client: TestClient,
    world: StudyUnitWorld,
    test_item_id: int,
    user_id: str,
    answers: list[object],
) -> tuple[int, object]:
    response = client.post(
        "/review-test-item",
        json=review_payload(test_item_id, world.test_session_id, answers),
        headers=authorization(user_id),
    )

    return response.status_code, response.json()


def test_review_test_item_refuses_a_strangers_item_exactly_like_an_absent_one(
    client: TestClient, world: StudyUnitWorld
) -> None:
    stranger = _posted_review(
        client,
        world,
        world.test_item_id,
        str(world.stranger),
        _CHOSEN_OPTION,
    )
    absent = _posted_review(
        client, world, ABSENT_ROW_ID, str(world.owner), _CHOSEN_OPTION
    )

    assert stranger == absent
    assert stranger == (NOT_FOUND, {"detail": MISSING_TEST_ITEM_DETAIL})


def test_refused_test_item_review_writes_nothing(
    client: TestClient,
    sessions: sessionmaker[Session],
    world: StudyUnitWorld,
) -> None:
    _ = _posted_review(
        client,
        world,
        world.test_item_id,
        str(world.stranger),
        _CHOSEN_OPTION,
    )

    with sessions() as session:
        assert session.query(TestItemReview).count() == 0


def test_a_refused_review_leaves_an_existing_review_untouched(
    client: TestClient,
    sessions: sessionmaker[Session],
    world: StudyUnitWorld,
) -> None:
    _ = _posted_review(
        client, world, world.test_item_id, str(world.owner), _CHOSEN_OPTION
    )

    with sessions() as session:
        before = session.query(TestItemReview).one()
        stored = (before.answers, before.reviewed_at, before.accuracy)

    _ = _posted_review(
        client,
        world,
        world.test_item_id,
        str(world.stranger),
        _OTHER_OPTION,
    )

    with sessions() as session:
        after = session.query(TestItemReview).one()

        assert (after.answers, after.reviewed_at, after.accuracy) == stored


def test_ownership_is_checked_before_any_write(
    client: TestClient,
    sessions: sessionmaker[Session],
    world: StudyUnitWorld,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        assessment_router, "owned_test_item", refusing_item_lookup
    )
    status_code, _ = _posted_review(
        client, world, world.test_item_id, str(world.owner), _CHOSEN_OPTION
    )

    with sessions() as session:
        assert session.query(TestItemReview).count() == 0

    assert status_code == NOT_FOUND


def test_review_test_item_loads_the_item_once(
    client: TestClient,
    world: StudyUnitWorld,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    lookup = _CountingItemLookup()
    recorder = _RecordingGet(cast("_SessionGet", Session.get))
    monkeypatch.setattr(assessment_router, "owned_test_item", lookup)
    monkeypatch.setattr(Session, "get", recorder)
    status_code, _ = _posted_review(
        client, world, world.test_item_id, str(world.owner), _CHOSEN_OPTION
    )

    assert status_code == OK
    assert lookup.calls == [(str(world.owner), world.test_item_id)]
    assert TestItem not in recorder.loaded_entities


def test_accuracy_comes_from_evaluate_accuracy_on_the_owned_item(
    client: TestClient,
    sessions: sessionmaker[Session],
    world: StudyUnitWorld,
) -> None:
    _ = _posted_review(
        client, world, world.test_item_id, str(world.owner), _CHOSEN_OPTION
    )

    with sessions() as session:
        item = session.get(TestItem, world.test_item_id)
        review = session.query(TestItemReview).one()

        assert item is not None
        assert review.accuracy == evaluate_accuracy(
            _CHOSEN_OPTION, item.type, item.content
        )
