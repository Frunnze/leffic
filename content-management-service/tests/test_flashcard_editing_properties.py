import uuid

import pytest
from fastapi import HTTPException
from hypothesis import given, settings
from hypothesis import strategies as st

from features.study_units.flashcard_editing_router import _owned_flashcard
from shared.models import Flashcard
from tests.property_support import property_world, seeded_deck
from tests.support import authorization

_OK = 200
_NOT_FOUND = 404
_CLIENT, _SESSIONS = property_world()
_CONTENTS = st.fixed_dictionaries(
    {"front": st.text(max_size=8), "back": st.text(max_size=8)}
)


@settings(max_examples=25, deadline=None)
@given(st.uuids(), st.uuids())
def test__owned_flashcard_property_never_reaches_a_strangers_card(
    owner: uuid.UUID, stranger: uuid.UUID
) -> None:
    with _SESSIONS() as session:
        _, _, card_ids = seeded_deck(session, owner, 1)

        assert (
            _owned_flashcard(session, str(owner), card_ids[0]).id
            == card_ids[0]
        )

        with pytest.raises(HTTPException) as raised:
            _ = _owned_flashcard(session, str(stranger), card_ids[0])

    assert raised.value.status_code == _NOT_FOUND


@settings(max_examples=25, deadline=None)
@given(st.uuids(), _CONTENTS)
def test_update_flashcard_property_round_trips_the_content_it_stored(
    owner: uuid.UUID, content: dict[str, str]
) -> None:
    with _SESSIONS() as session:
        _, _, card_ids = seeded_deck(session, owner, 1)

    response = _CLIENT.patch(
        "/update-flashcard",
        json={"flashcard_id": card_ids[0], "content": content},
        headers=authorization(str(owner)),
    )

    with _SESSIONS() as session:
        stored = session.get(Flashcard, card_ids[0])

        assert stored is not None
        assert stored.content == content

    assert response.status_code == _OK


@settings(max_examples=25, deadline=None)
@given(st.uuids(), st.uuids())
def test_delete_flashcard_property_removes_only_the_owners_card(
    owner: uuid.UUID, stranger: uuid.UUID
) -> None:
    with _SESSIONS() as session:
        _, _, card_ids = seeded_deck(session, owner, 1)

    refused = _CLIENT.delete(
        "/delete-flashcard/",
        params={"flashcard_id": card_ids[0]},
        headers=authorization(str(stranger)),
    )
    removed = _CLIENT.delete(
        "/delete-flashcard/",
        params={"flashcard_id": card_ids[0]},
        headers=authorization(str(owner)),
    )

    with _SESSIONS() as session:
        assert session.get(Flashcard, card_ids[0]) is None

    assert refused.status_code == _NOT_FOUND
    assert removed.status_code == _OK
