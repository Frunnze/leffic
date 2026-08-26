from typing import Final
from unittest import mock

import pytest
from fastapi import HTTPException
from hypothesis import given, settings
from hypothesis import strategies as st
from sqlalchemy.orm import Session, sessionmaker

from features.study_units_generation import task_status_router
from features.study_units_generation.task_ownership import (
    MISSING_TASK,
    signed_task_id,
)
from features.study_units_generation.task_status_router import (
    _owned_task_id,
    get_flashcard_status,
    get_note_task_status,
    get_test_task_status,
)
from tests.access_support import HOME_ID, OwnedContent, seeded_content
from tests.support import OTHER_USER_ID, USER_ID, in_memory_sessions
from tests.task_token_support import (
    CELERY_TASK_ID,
    NOT_FOUND,
    PENDING,
    PendingAsyncResult,
    RefusingAsyncResult,
    forged_token,
    owned_token,
)

_CELERY_IDENTIFIERS: Final[st.SearchStrategy[str]] = st.text(
    alphabet="abcdef0123456789-", min_size=1, max_size=40
)
_EXAMPLE_BUDGET: Final[int] = 25


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    return in_memory_sessions()


@pytest.fixture
def owned(sessions: sessionmaker[Session]) -> OwnedContent:
    return seeded_content(sessions, HOME_ID)


def test_another_user_cannot_resolve_a_token_for_that_folder(
    sessions: sessionmaker[Session], owned: OwnedContent
) -> None:
    with sessions() as session, pytest.raises(HTTPException) as refusal:
        _ = _owned_task_id(
            task_id=owned_token(owned.folder_id),
            user_id=OTHER_USER_ID,
            db=session,
        )

    assert refusal.value.status_code == NOT_FOUND
    assert refusal.value.detail == MISSING_TASK


def test_a_forged_token_is_refused_before_the_folder_is_queried(
    sessions: sessionmaker[Session], owned: OwnedContent
) -> None:
    with sessions() as session, pytest.raises(HTTPException) as refusal:
        _ = _owned_task_id(
            task_id=forged_token(owned.folder_id),
            user_id=USER_ID,
            db=session,
        )

    assert refusal.value.detail == MISSING_TASK


def test_the_flashcard_handler_reports_pending_for_its_owner(
    sessions: sessionmaker[Session], owned: OwnedContent
) -> None:
    celery = PendingAsyncResult()

    with sessions() as session, mock.patch.object(
        task_status_router, "AsyncResult", celery
    ):
        reported = get_flashcard_status(
            task_id=_owned_task_id(
                task_id=owned_token(owned.folder_id),
                user_id=USER_ID,
                db=session,
            ),
            db=session,
        )

    assert reported == {"status": PENDING}
    assert celery.looked_up == [CELERY_TASK_ID]


def test_the_test_handler_reports_pending_for_its_owner(
    sessions: sessionmaker[Session], owned: OwnedContent
) -> None:
    celery = PendingAsyncResult()

    with sessions() as session, mock.patch.object(
        task_status_router, "AsyncResult", celery
    ):
        reported = get_test_task_status(
            task_id=_owned_task_id(
                task_id=owned_token(owned.folder_id),
                user_id=USER_ID,
                db=session,
            ),
            db=session,
        )

    assert reported == {"status": PENDING}
    assert celery.looked_up == [CELERY_TASK_ID]


def test_the_note_handler_reports_pending_for_its_owner(
    sessions: sessionmaker[Session], owned: OwnedContent
) -> None:
    celery = PendingAsyncResult()

    with sessions() as session, mock.patch.object(
        task_status_router, "AsyncResult", celery
    ):
        reported = get_note_task_status(
            task_id=_owned_task_id(
                task_id=owned_token(owned.folder_id),
                user_id=USER_ID,
                db=session,
            )
        )

    assert reported == {"status": PENDING}
    assert celery.looked_up == [CELERY_TASK_ID]


def test_a_refused_token_never_reaches_celery(
    sessions: sessionmaker[Session], owned: OwnedContent
) -> None:
    with sessions() as session, mock.patch.object(
        task_status_router, "AsyncResult", RefusingAsyncResult()
    ), pytest.raises(HTTPException) as refusal:
        _ = _owned_task_id(
            task_id=forged_token(owned.folder_id),
            user_id=USER_ID,
            db=session,
        )

    assert refusal.value.detail == MISSING_TASK


@settings(max_examples=_EXAMPLE_BUDGET, deadline=None)
@given(_CELERY_IDENTIFIERS)
def test__owned_task_id_property_unwraps_a_token_its_owner_minted(
    celery_task_id: str,
) -> None:
    sessions = in_memory_sessions()
    owned = seeded_content(sessions, HOME_ID)

    with sessions() as session:
        resolved = _owned_task_id(
            task_id=signed_task_id(celery_task_id, owned.folder_id),
            user_id=USER_ID,
            db=session,
        )

    assert resolved == celery_task_id
