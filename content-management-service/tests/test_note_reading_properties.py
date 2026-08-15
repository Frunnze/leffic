import uuid
from typing import cast

from hypothesis import given, settings
from hypothesis import strategies as st

from shared.models import Note
from tests.folder_seeding import seeded_folder
from tests.property_support import property_world
from tests.support import authorization

_OK = 200
_NOT_FOUND = 404
_CLIENT, _SESSIONS = property_world()
_NOTE_COUNTS = st.integers(min_value=1, max_value=3)


def _seeded_note(owner: uuid.UUID) -> uuid.UUID:
    with _SESSIONS() as session:
        folder_id = seeded_folder(session, owner, {"note": 1})
        note = (
            session.query(Note).filter(Note.folder_id == folder_id).first()
        )

        assert note is not None

        return note.id


@settings(max_examples=25, deadline=None)
@given(st.uuids(), st.uuids())
def test_get_note_property_shows_a_note_only_to_its_owner(
    owner: uuid.UUID, stranger: uuid.UUID
) -> None:
    note_id = _seeded_note(owner)
    mine = _CLIENT.get(
        "/note",
        params={"note_id": str(note_id)},
        headers=authorization(str(owner)),
    )
    theirs = _CLIENT.get(
        "/note",
        params={"note_id": str(note_id)},
        headers=authorization(str(stranger)),
    )
    body = cast("dict[str, object]", mine.json())

    assert mine.status_code == _OK
    assert body["read"] is False
    assert theirs.status_code == _NOT_FOUND


@settings(max_examples=25, deadline=None)
@given(st.uuids())
def test_review_note_property_marks_the_note_read_and_stays_read(
    owner: uuid.UUID,
) -> None:
    note_id = _seeded_note(owner)

    for _ in range(2):
        reviewed = _CLIENT.post(
            "/review-note",
            json={"note_id": str(note_id)},
            headers=authorization(str(owner)),
        )

        assert reviewed.status_code == _OK

    read_back = _CLIENT.get(
        "/note",
        params={"note_id": str(note_id)},
        headers=authorization(str(owner)),
    )
    body = cast("dict[str, object]", read_back.json())

    assert body["read"] is True


@settings(max_examples=25, deadline=None)
@given(st.uuids(), _NOTE_COUNTS)
def test_get_notes_stats_property_splits_every_note_into_due_or_read(
    owner: uuid.UUID, note_count: int
) -> None:
    with _SESSIONS() as session:
        folder_id = seeded_folder(session, owner, {"note": note_count})

    response = _CLIENT.get(
        "/notes-stats",
        params={"folder_id": str(folder_id)},
        headers=authorization(str(owner)),
    )
    body = cast("dict[str, int]", response.json())

    assert response.status_code == _OK
    assert body["due"] + body["read"] == note_count
