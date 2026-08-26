from collections.abc import Iterator
from typing import Final

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from features.study_units_generation import task_status_router
from features.study_units_generation.task_ownership import (
    MISSING_TASK,
    signed_task_id,
)
from tests.access_support import (
    HOME_ID,
    OwnedContent,
    crashless_client,
    identifier_spellings,
    seeded_content,
)
from tests.hostile_identifiers import (
    SINGLE_SEGMENT_IDENTIFIERS,
    TRANSPORT_MANGLED_IDENTIFIERS,
    TRANSPORT_STABLE_IDENTIFIERS,
)
from tests.support import OTHER_USER_ID, authorization, in_memory_sessions
from tests.task_token_support import (
    CELERY_TASK_ID,
    NOT_FOUND,
    SERVER_ERROR_FLOOR,
    STATUS_PATHS,
    PendingAsyncResult,
    answered_details,
)

_EXPECTED_REFUSAL: Final[set[tuple[int, str]]] = {
    (NOT_FOUND, MISSING_TASK)
}
_LONG_SEGMENT: Final[str] = "9" * 4096
_NULL_BYTE_SEGMENT: Final[str] = "folder\x00id"


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    return in_memory_sessions()


@pytest.fixture
def client(sessions: sessionmaker[Session]) -> Iterator[TestClient]:
    yield from crashless_client(sessions)


@pytest.fixture
def owned(sessions: sessionmaker[Session]) -> OwnedContent:
    return seeded_content(sessions, HOME_ID)


@pytest.fixture(autouse=True)
def celery(monkeypatch: pytest.MonkeyPatch) -> PendingAsyncResult:
    pending = PendingAsyncResult()
    monkeypatch.setattr(task_status_router, "AsyncResult", pending)

    return pending


def _signed_over(folder_segments: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(
        signed_task_id(CELERY_TASK_ID, segment)
        for segment in folder_segments
    )


def _signed_task_segments(
    task_segments: tuple[str, ...], folder_id: str
) -> tuple[str, ...]:
    return tuple(
        signed_task_id(task_segment, folder_id)
        for task_segment in task_segments
    )


@pytest.mark.usefixtures("owned")
@pytest.mark.parametrize("path", STATUS_PATHS)
def test_a_signed_hostile_folder_segment_is_refused(
    client: TestClient, path: str
) -> None:
    tokens = _signed_over(SINGLE_SEGMENT_IDENTIFIERS)

    assert answered_details(
        client, path, tokens, authorization()
    ) == _EXPECTED_REFUSAL


@pytest.mark.usefixtures("owned")
@pytest.mark.parametrize("path", STATUS_PATHS)
def test_a_signed_oversized_folder_segment_is_refused(
    client: TestClient, path: str
) -> None:
    tokens = _signed_over((_LONG_SEGMENT, _NULL_BYTE_SEGMENT, ""))

    assert answered_details(
        client, path, tokens, authorization()
    ) == _EXPECTED_REFUSAL


@pytest.mark.parametrize("path", STATUS_PATHS)
def test_a_signed_hostile_task_segment_reaches_celery_verbatim(
    client: TestClient,
    owned: OwnedContent,
    path: str,
    celery: PendingAsyncResult,
) -> None:
    tokens = _signed_task_segments(
        TRANSPORT_STABLE_IDENTIFIERS, owned.folder_id
    )
    statuses = {
        code
        for code, _detail in answered_details(
            client, path, tokens, authorization()
        )
    }

    assert max(statuses) < SERVER_ERROR_FLOOR
    assert celery.looked_up == list(TRANSPORT_STABLE_IDENTIFIERS)


@pytest.mark.parametrize("path", STATUS_PATHS)
def test_a_task_segment_the_transport_alters_is_refused(
    client: TestClient,
    owned: OwnedContent,
    path: str,
    celery: PendingAsyncResult,
) -> None:
    tokens = _signed_task_segments(
        TRANSPORT_MANGLED_IDENTIFIERS, owned.folder_id
    )

    assert answered_details(
        client, path, tokens, authorization()
    ) == _EXPECTED_REFUSAL
    assert celery.looked_up == []


@pytest.mark.usefixtures("owned")
@pytest.mark.parametrize("path", STATUS_PATHS)
def test_a_signed_home_folder_of_another_user_is_refused(
    client: TestClient, path: str
) -> None:
    tokens = _signed_over(identifier_spellings(OTHER_USER_ID))

    assert answered_details(
        client, path, tokens, authorization()
    ) == _EXPECTED_REFUSAL


@pytest.mark.parametrize("path", STATUS_PATHS)
def test_an_owned_token_presented_by_a_stranger_is_refused(
    client: TestClient, owned: OwnedContent, path: str
) -> None:
    tokens = _signed_over(identifier_spellings(owned.folder_id))
    stranger = authorization(OTHER_USER_ID)

    assert answered_details(
        client, path, tokens, stranger
    ) == _EXPECTED_REFUSAL
