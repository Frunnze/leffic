import uuid
from datetime import UTC, datetime
from typing import cast

from hypothesis import given, settings
from hypothesis import strategies as st

from shared.models import Test, TestItem, TestSession
from tests.folder_seeding import seeded_folder
from tests.property_support import property_world, seeded_deck
from tests.support import authorization

_OK = 200
_NOT_FOUND = 404
_DONE = "done"
_CLIENT, _SESSIONS = property_world()
_COUNTS = st.integers(min_value=1, max_value=3)


def _seeded_quiz(owner: uuid.UUID, item_count: int) -> uuid.UUID:
    with _SESSIONS() as session:
        folder_id = seeded_folder(session, owner, {})
        quiz = Test(
            id=uuid.uuid4(),
            name="Quiz",
            folder_id=folder_id,
            created_at=datetime.now(UTC),
            public=False,
        )

        for index in range(item_count):
            quiz.test_items.append(
                TestItem(
                    content={"question": f"q{index}"},
                    type="multiple_choice",
                    created_at=datetime.now(UTC),
                )
            )

        session.add(quiz)
        session.commit()

        return folder_id


@settings(max_examples=25, deadline=None)
@given(st.uuids(), _COUNTS)
def test_test_items_stats_property_counts_every_item_under_the_folder(
    owner: uuid.UUID, item_count: int
) -> None:
    folder_id = _seeded_quiz(owner, item_count)
    response = _CLIENT.get(
        "/test-items-stats",
        params={"folder_id": str(folder_id)},
        headers=authorization(str(owner)),
    )
    body = cast("dict[str, int]", response.json())

    assert response.status_code == _OK
    assert body["total"] == item_count
    assert body["correct"] == 0


@settings(max_examples=25, deadline=None)
@given(st.uuids())
def test_test_items_stats_property_reports_an_empty_folder_as_missing(
    owner: uuid.UUID,
) -> None:
    with _SESSIONS() as session:
        folder_id = seeded_folder(session, owner, {})

    response = _CLIENT.get(
        "/test-items-stats",
        params={"folder_id": str(folder_id)},
        headers=authorization(str(owner)),
    )

    assert response.status_code == _NOT_FOUND


@settings(max_examples=25, deadline=None)
@given(st.uuids())
def test_test_session_results_property_closes_the_session_it_reports_on(
    owner: uuid.UUID,
) -> None:
    with _SESSIONS() as session:
        opened = TestSession(
            id=uuid.uuid4(), origin_id=str(uuid.uuid4()), status="ongoing"
        )
        session.add(opened)
        session.commit()
        session_id = opened.id

    response = _CLIENT.get(
        "/test-session-results",
        params={"test_session": str(session_id)},
        headers=authorization(str(owner)),
    )

    with _SESSIONS() as session:
        closed = session.get(TestSession, session_id)

        assert closed is not None
        assert closed.status == _DONE

    assert response.status_code == _NOT_FOUND


@settings(max_examples=25, deadline=None)
@given(st.uuids(), _COUNTS)
def test_get_flashcards_stats_property_splits_cards_into_due_and_done(
    owner: uuid.UUID, card_count: int
) -> None:
    with _SESSIONS() as session:
        folder_id, _, _ = seeded_deck(session, owner, card_count)

    response = _CLIENT.get(
        "/flashcards-stats",
        params={"folder_id": str(folder_id)},
        headers=authorization(str(owner)),
    )
    body = cast("dict[str, int]", response.json())

    assert response.status_code == _OK
    assert body["due"] + body["done"] == card_count
