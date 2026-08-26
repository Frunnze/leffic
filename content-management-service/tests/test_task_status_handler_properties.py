import uuid
from typing import Final
from unittest import mock

from hypothesis import given, settings
from hypothesis import strategies as st

from features.study_units_generation import task_status_router
from features.study_units_generation.task_ownership import signed_task_id
from features.study_units_generation.task_status_router import (
    _owned_task_id,
    get_flashcard_status,
    get_note_task_status,
)
from tests.folder_seeding import seeded_folder
from tests.property_fakes import FakeAsyncResult
from tests.support import in_memory_sessions

_SUCCEEDED: Final[str] = "SUCCESS"
_UNFINISHED: Final[st.SearchStrategy[str]] = st.sampled_from(
    ["PENDING", "STARTED", "RETRY", "FAILURE"]
)
_TASK_IDS: Final[st.SearchStrategy[str]] = st.text(
    alphabet="abcdef0123456789", min_size=4, max_size=12
)
_NAMES: Final[st.SearchStrategy[str]] = st.text(min_size=1, max_size=10)
_SESSIONS = in_memory_sessions()


def _reporting(
    status: str, result: object, *, ready: bool
) -> FakeAsyncResult:
    return FakeAsyncResult(status, result, finished=ready)

@settings(max_examples=25, deadline=None)
@given(_TASK_IDS, st.uuids(), _NAMES, _NAMES)
def test_get_note_task_status_property_describes_a_finished_note(
    task_id: str, owner: uuid.UUID, note_id: str, note_name: str
) -> None:
    finished = {"note_id": note_id, "note_name": note_name}

    with _SESSIONS() as session:
        folder_id = seeded_folder(session, owner, {})
        owned = _owned_task_id(
            task_id=signed_task_id(task_id, str(folder_id)),
            user_id=str(owner),
            db=session,
        )

        with mock.patch.object(
            task_status_router,
            "AsyncResult",
            _reporting(_SUCCEEDED, finished, ready=True),
        ):
            described = get_note_task_status(task_id=owned)

    assert described["type"] == "note"
    assert described["note_id"] == note_id
    assert described["name"] == note_name


@settings(max_examples=25, deadline=None)
@given(_TASK_IDS, st.uuids(), _UNFINISHED)
def test_get_flashcard_status_property_reports_only_a_status_while_running(
    task_id: str, owner: uuid.UUID, status: str
) -> None:
    with _SESSIONS() as session:
        folder_id = seeded_folder(session, owner, {})
        owned = _owned_task_id(
            task_id=signed_task_id(task_id, str(folder_id)),
            user_id=str(owner),
            db=session,
        )

        with mock.patch.object(
            task_status_router,
            "AsyncResult",
            _reporting(status, None, ready=False),
        ):
            reported = get_flashcard_status(
                task_id=owned, db=session
            )

    assert reported == {"status": status}
