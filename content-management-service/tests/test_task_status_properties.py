import uuid
from unittest import mock

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from features.study_units_generation import task_status_router
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
    _finished_result,
    get_flashcard_status,
    get_note_task_status,
    get_test_task_status,
)
from tests.folder_seeding import seeded_folder
from tests.property_fakes import FakeAsyncResult
from tests.support import in_memory_sessions

_SUCCEEDED = "SUCCESS"
_UNFINISHED = st.sampled_from(["PENDING", "STARTED", "RETRY", "FAILURE"])
_TASK_IDS = st.text(alphabet="abcdef0123456789", min_size=4, max_size=12)
_NAMES = st.text(min_size=1, max_size=10)
_SESSIONS = in_memory_sessions()
_NO_SOURCE = StudyUnitSource(kind=None, reference=None)


def _reporting(
    status: str, result: object, *, ready: bool
) -> FakeAsyncResult:
    return FakeAsyncResult(status, result, finished=ready)


@settings(max_examples=50)
@given(_TASK_IDS, _UNFINISHED)
def test__finished_result_property_withholds_a_result_until_it_succeeds(
    task_id: str, status: str
) -> None:
    with mock.patch.object(
        task_status_router,
        "AsyncResult",
        _reporting(status, {"anything": 1}, ready=True),
    ):
        assert _finished_result(task_id) == (status, None)


@settings(max_examples=50)
@given(_TASK_IDS, st.dictionaries(_NAMES, _NAMES, max_size=3))
def test__finished_result_property_hands_over_a_finished_mapping(
    task_id: str, finished: dict[str, str]
) -> None:
    with mock.patch.object(
        task_status_router,
        "AsyncResult",
        _reporting(_SUCCEEDED, finished, ready=True),
    ):
        assert _finished_result(task_id) == (_SUCCEEDED, finished)


@settings(max_examples=25)
@given(_TASK_IDS, st.one_of(st.text(max_size=5), st.integers(), st.none()))
def test__finished_result_property_refuses_a_result_that_is_not_a_mapping(
    task_id: str, finished: object
) -> None:
    with mock.patch.object(
        task_status_router,
        "AsyncResult",
        _reporting(_SUCCEEDED, finished, ready=True),
    ), pytest.raises(TypeError):
        _ = _finished_result(task_id)


@settings(max_examples=25, deadline=None)
@given(_TASK_IDS, st.uuids(), _NAMES)
def test_get_flashcard_status_property_describes_a_finished_deck(
    task_id: str, owner: uuid.UUID, deck_name: str
) -> None:
    with _SESSIONS() as session:
        folder_id = seeded_folder(session, owner, {})
        deck_id = create_flashcard_deck(
            session, str(folder_id), _NO_SOURCE
        )
        _ = name_deck_once(session, deck_id, deck_name)
        finished = {"flashcard_deck_id": deck_id, "type": "basic"}

        with mock.patch.object(
            task_status_router,
            "AsyncResult",
            _reporting(_SUCCEEDED, finished, ready=True),
        ):
            described = get_flashcard_status(task_id, session)

    assert described["type"] == "flashcard_deck"
    assert described["flashcard_deck_id"] == deck_id
    assert described["flashcard_type"] == "basic"
    assert described["name"] == deck_name


@settings(max_examples=25, deadline=None)
@given(_TASK_IDS, st.uuids(), _NAMES)
def test_get_test_task_status_property_describes_a_finished_test(
    task_id: str, owner: uuid.UUID, test_name: str
) -> None:
    with _SESSIONS() as session:
        folder_id = seeded_folder(session, owner, {})
        test_id = create_test(session, str(folder_id), _NO_SOURCE)
        _ = name_test_once(session, test_id, test_name)
        finished = {"test_id": test_id, "type": "short_answer"}

        with mock.patch.object(
            task_status_router,
            "AsyncResult",
            _reporting(_SUCCEEDED, finished, ready=True),
        ):
            described = get_test_task_status(task_id, session)

    assert described["type"] == "test"
    assert described["test_id"] == test_id
    assert described["test_item_type"] == "short_answer"
    assert described["name"] == test_name


@settings(max_examples=25)
@given(_TASK_IDS, _NAMES, _NAMES)
def test_get_note_task_status_property_describes_a_finished_note(
    task_id: str, note_id: str, note_name: str
) -> None:
    finished = {"note_id": note_id, "note_name": note_name}

    with mock.patch.object(
        task_status_router,
        "AsyncResult",
        _reporting(_SUCCEEDED, finished, ready=True),
    ):
        described = get_note_task_status(task_id)

    assert described["type"] == "note"
    assert described["note_id"] == note_id
    assert described["name"] == note_name


@settings(max_examples=25)
@given(_TASK_IDS, _UNFINISHED)
def test_get_flashcard_status_property_reports_only_a_status_while_running(
    task_id: str, status: str
) -> None:
    with _SESSIONS() as session, mock.patch.object(
        task_status_router,
        "AsyncResult",
        _reporting(status, None, ready=False),
    ):
        assert get_flashcard_status(task_id, session) == {
            "status": status
        }
