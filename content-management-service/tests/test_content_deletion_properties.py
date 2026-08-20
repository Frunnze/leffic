import uuid

from hypothesis import given, settings
from hypothesis import strategies as st

from shared.models import FlashcardDeck, Note, Test
from tests.folder_seeding import seeded_folder
from tests.property_support import property_world, seeded_file
from tests.support import authorization

_OK = 200
_NOT_FOUND = 404
_CLIENT, _SESSIONS = property_world()

GeneratedUnit = FlashcardDeck | Test | Note


def _seeded_unit(
    owner: uuid.UUID, model: type[GeneratedUnit], kind: str
) -> uuid.UUID:
    with _SESSIONS() as session:
        folder_id = seeded_folder(session, owner, {kind: 1})
        row = (
            session.query(model)
            .filter(model.folder_id == folder_id)
            .first()
        )

        assert row is not None

        return row.id


@settings(max_examples=25, deadline=None)
@given(st.uuids(), st.uuids())
def test_delete_deck_property_removes_only_the_owners_deck(
    owner: uuid.UUID, stranger: uuid.UUID
) -> None:
    deck_id = _seeded_unit(owner, FlashcardDeck, "flashcard_deck")
    refused = _CLIENT.delete(
        "/delete-deck/",
        params={"deck_id": str(deck_id)},
        headers=authorization(str(stranger)),
    )
    removed = _CLIENT.delete(
        "/delete-deck/",
        params={"deck_id": str(deck_id)},
        headers=authorization(str(owner)),
    )

    assert refused.status_code == _NOT_FOUND
    assert removed.status_code == _OK


@settings(max_examples=25, deadline=None)
@given(st.uuids(), st.uuids())
def test_delete_test_property_removes_only_the_owners_test(
    owner: uuid.UUID, stranger: uuid.UUID
) -> None:
    test_id = _seeded_unit(owner, Test, "test")
    refused = _CLIENT.delete(
        "/delete-test/",
        params={"test_id": str(test_id)},
        headers=authorization(str(stranger)),
    )
    removed = _CLIENT.delete(
        "/delete-test/",
        params={"test_id": str(test_id)},
        headers=authorization(str(owner)),
    )

    assert refused.status_code == _NOT_FOUND
    assert removed.status_code == _OK


@settings(max_examples=25, deadline=None)
@given(st.uuids(), st.uuids())
def test_delete_note_property_removes_only_the_owners_note(
    owner: uuid.UUID, stranger: uuid.UUID
) -> None:
    note_id = _seeded_unit(owner, Note, "note")
    refused = _CLIENT.delete(
        "/delete-note/",
        params={"note_id": str(note_id)},
        headers=authorization(str(stranger)),
    )
    removed = _CLIENT.delete(
        "/delete-note/",
        params={"note_id": str(note_id)},
        headers=authorization(str(owner)),
    )

    assert refused.status_code == _NOT_FOUND
    assert removed.status_code == _OK


@settings(max_examples=25, deadline=None)
@given(st.uuids(), st.uuids())
def test_delete_file_property_removes_only_the_owners_file(
    owner: uuid.UUID, stranger: uuid.UUID
) -> None:
    with _SESSIONS() as session:
        file_id = seeded_file(session, owner)

    refused = _CLIENT.delete(
        "/delete-file/",
        params={"file_id": str(file_id)},
        headers=authorization(str(stranger)),
    )
    removed = _CLIENT.delete(
        "/delete-file/",
        params={"file_id": str(file_id)},
        headers=authorization(str(owner)),
    )

    assert refused.status_code == _NOT_FOUND
    assert removed.status_code == _OK
