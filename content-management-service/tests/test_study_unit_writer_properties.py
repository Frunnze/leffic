import uuid
from typing import cast

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from features.study_units_generation.study_unit_source import (
    StudyUnitSource,
)
from features.study_units_generation.study_unit_writer import (
    MissingFolderError,
    existing_folder,
    generated_records,
    save_note,
)
from shared.models import Note
from tests.folder_seeding import seeded_folder
from tests.support import in_memory_sessions

_MISSING_FOLDER = "Folder does not exist!"
_SESSIONS = in_memory_sessions()
_NO_SOURCE = StudyUnitSource(kind=None, reference=None)
_RECORD = st.fixed_dictionaries({"front": st.text(max_size=6)})


@settings(max_examples=50)
@given(
    st.one_of(
        st.lists(st.one_of(_RECORD, st.integers(), st.none()), max_size=5),
        st.text(max_size=5),
        st.integers(),
        st.none(),
    )
)
def test_generated_records_property_keeps_exactly_the_mappings(
    generated: object,
) -> None:
    kept = generated_records(generated)

    if isinstance(generated, list):
        assert kept == [
            record
            for record in cast("list[object]", generated)
            if isinstance(record, dict)
        ]
    else:
        assert kept == []


@settings(max_examples=25, deadline=None)
@given(st.uuids(), st.uuids())
def test_existing_folder_property_refuses_a_folder_that_is_not_there(
    owner: uuid.UUID, absent: uuid.UUID
) -> None:
    with _SESSIONS() as session:
        folder_id = seeded_folder(session, owner, {})

        assert existing_folder(session, str(folder_id)).id == folder_id

        with pytest.raises(MissingFolderError, match=_MISSING_FOLDER):
            _ = existing_folder(session, str(absent))


@settings(max_examples=25, deadline=None)
@given(st.uuids(), st.text(max_size=12), st.text(max_size=20))
def test_save_note_property_round_trips_the_name_and_the_body(
    owner: uuid.UUID, name: str, body: str
) -> None:
    with _SESSIONS() as session:
        folder_id = seeded_folder(session, owner, {})
        note_id = save_note(
            session, str(folder_id), name, body, _NO_SOURCE
        )
        saved = session.get(Note, uuid.UUID(note_id))

        assert saved is not None
        assert saved.name == name
        assert saved.content == body


@settings(max_examples=25)
@given(st.integers(min_value=1, max_value=3))
def test___init___property_always_names_the_missing_folder(
    count: int,
) -> None:
    errors = [MissingFolderError() for _ in range(count)]

    assert all(str(error) == _MISSING_FOLDER for error in errors)
