import inspect
from typing import cast

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from features.study_units import flashcard_editing_router, flashcard_router
from shared.models import Flashcard, FlashcardReview
from tests.study_unit_access_support import (
    ABSENT_ROW_ID,
    MISSING_FLASHCARD_DETAIL,
    NOT_FOUND,
    OK,
    StudyUnitWorld,
    refusing_flashcard_lookup,
)
from tests.support import authorization

_REVIEW_BODY_KEYS = {"due_date", "new_fsrs_card"}
_GOOD_RATING = 3


class _RecordingLookup:
    def __init__(self) -> None:
        self.calls: list[tuple[str, int]] = []

    def __call__(
        self, db: Session, user_id: str, flashcard_id: int
    ) -> Flashcard | None:
        self.calls.append((user_id, flashcard_id))

        return db.get(Flashcard, flashcard_id)

def _reviewed(
    client: TestClient, flashcard_id: int, headers: dict[str, str]
) -> tuple[int, object]:
    response = client.post(
        "/review-flashcard",
        json={"flashcard_id": flashcard_id, "rating": _GOOD_RATING},
        headers=headers,
    )

    return response.status_code, response.json()


def test_review_flashcard_refuses_a_strangers_card_exactly_like_an_absent_one(
    client: TestClient, world: StudyUnitWorld
) -> None:
    stranger = _reviewed(
        client, world.flashcard_id, authorization(str(world.stranger))
    )
    absent = _reviewed(
        client, ABSENT_ROW_ID, authorization(str(world.owner))
    )

    assert stranger == absent
    assert stranger == (NOT_FOUND, {"detail": MISSING_FLASHCARD_DETAIL})


def test_refused_flashcard_review_writes_nothing(
    client: TestClient,
    sessions: sessionmaker[Session],
    world: StudyUnitWorld,
) -> None:
    _ = _reviewed(
        client, world.flashcard_id, authorization(str(world.stranger))
    )

    with sessions() as session:
        card = session.get(Flashcard, world.flashcard_id)

        assert card is not None
        assert card.fsrs_card is None
        assert card.next_review is None
        assert session.query(FlashcardReview).count() == 0


def test_owner_flashcard_review_body_is_unchanged(
    client: TestClient, world: StudyUnitWorld
) -> None:
    status_code, body = _reviewed(
        client, world.flashcard_id, authorization(str(world.owner))
    )

    assert status_code == OK
    assert isinstance(body, dict)
    assert set(cast("dict[str, object]", body)) == _REVIEW_BODY_KEYS


def test_review_flashcard_delegates_to_owned_flashcard(
    client: TestClient,
    world: StudyUnitWorld,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    lookup = _RecordingLookup()
    monkeypatch.setattr(flashcard_router, "owned_flashcard", lookup)
    status_code, _ = _reviewed(
        client, world.flashcard_id, authorization(str(world.owner))
    )

    assert status_code == OK
    assert lookup.calls == [(str(world.owner), world.flashcard_id)]


def test_review_flashcard_has_no_lookup_that_bypasses_the_owner_check(
    client: TestClient,
    sessions: sessionmaker[Session],
    world: StudyUnitWorld,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        flashcard_router, "owned_flashcard", refusing_flashcard_lookup
    )
    status_code, _ = _reviewed(
        client, world.flashcard_id, authorization(str(world.owner))
    )

    with sessions() as session:
        assert session.query(FlashcardReview).count() == 0

    assert status_code == NOT_FOUND


def test_flashcard_router_has_no_dead_detail_constant() -> None:
    assert not hasattr(flashcard_router, "_MISSING_FLASHCARD")


def test_flashcard_router_imports_no_unused_error_names() -> None:
    assert not hasattr(flashcard_router, "HTTPException")
    assert not hasattr(flashcard_router, "status")


def test_review_flashcard_stays_synchronous() -> None:
    assert not inspect.iscoroutinefunction(
        flashcard_router.review_flashcard
    )


def test_editing_router_reuses_the_shared_helper() -> None:
    assert not hasattr(flashcard_editing_router, "_owned_flashcard")
    assert not hasattr(flashcard_editing_router, "_MISSING_FLASHCARD")
    assert hasattr(flashcard_editing_router, "owned_flashcard")
