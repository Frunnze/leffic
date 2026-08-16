import uuid

from hypothesis import given, settings
from hypothesis import strategies as st

from features.study_units_generation.assessment_writer import (
    create_test,
    name_test_once,
)
from features.study_units_generation.flashcard_deck_writer import (
    create_flashcard_deck,
    name_deck_once,
)
from features.study_units_generation.study_unit_source import (
    StudyUnitSource,
)
from features.study_units_generation.task_status_router import (
    _as_identifier,
    _deck_name,
    _test_name,
)
from tests.folder_seeding import seeded_folder
from tests.support import in_memory_sessions

_SESSIONS = in_memory_sessions()
_NO_SOURCE = StudyUnitSource(kind=None, reference=None)
_NAMES = st.text(min_size=1, max_size=10)


@settings(max_examples=25, deadline=None)
@given(st.uuids(), st.uuids(), _NAMES)
def test__deck_name_property_answers_none_for_a_deck_that_is_gone(
    owner: uuid.UUID, absent: uuid.UUID, deck_name: str
) -> None:
    with _SESSIONS() as session:
        folder_id = seeded_folder(session, owner, {})
        deck_id = create_flashcard_deck(
            session, str(folder_id), _NO_SOURCE
        )
        _ = name_deck_once(session, deck_id, deck_name)

        assert _deck_name(session, deck_id) == deck_name
        assert _deck_name(session, str(absent)) is None


@settings(max_examples=25, deadline=None)
@given(st.uuids(), st.uuids(), _NAMES)
def test__test_name_property_answers_none_for_a_test_that_is_gone(
    owner: uuid.UUID, absent: uuid.UUID, test_name: str
) -> None:
    with _SESSIONS() as session:
        folder_id = seeded_folder(session, owner, {})
        test_id = create_test(session, str(folder_id), _NO_SOURCE)
        _ = name_test_once(session, test_id, test_name)

        assert _test_name(session, test_id) == test_name
        assert _test_name(session, str(absent)) is None


@settings(max_examples=50)
@given(st.text(max_size=12))
def test__as_identifier_property_answers_none_for_what_is_not_a_uuid(
    row_id: str,
) -> None:
    try:
        expected = uuid.UUID(row_id)
    except ValueError:
        expected = None

    assert _as_identifier(row_id) == expected


@settings(max_examples=50)
@given(st.uuids())
def test__as_identifier_property_round_trips_a_real_uuid(
    row_id: uuid.UUID,
) -> None:
    assert _as_identifier(str(row_id)) == row_id
