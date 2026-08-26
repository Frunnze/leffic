from collections.abc import Iterator
from typing import Final

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from features.study_units_generation import task_status_router
from features.study_units_generation.task_ownership import MISSING_TASK
from tests.access_support import (
    HOME_ID,
    OwnedContent,
    crashless_client,
    seeded_content,
)
from tests.hostile_identifiers import SINGLE_SEGMENT_IDENTIFIERS
from tests.support import authorization, in_memory_sessions
from tests.task_token_support import (
    CELERY_TASK_ID,
    FORGED_DIGEST,
    NOT_FOUND,
    SERVER_ERROR_FLOOR,
    STATUS_PATHS,
    PendingAsyncResult,
    answered_details,
    owned_token,
)

_EXPECTED_REFUSAL: Final[set[tuple[int, str]]] = {
    (NOT_FOUND, MISSING_TASK)
}


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
def unreachable_celery(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        task_status_router, "AsyncResult", PendingAsyncResult()
    )


def _hostile_task_segments(folder_id: str) -> tuple[str, ...]:
    return tuple(
        f"{hostile}.{folder_id}.{FORGED_DIGEST}"
        for hostile in SINGLE_SEGMENT_IDENTIFIERS
    )


def _hostile_folder_segments() -> tuple[str, ...]:
    return tuple(
        f"{CELERY_TASK_ID}.{hostile}.{FORGED_DIGEST}"
        for hostile in SINGLE_SEGMENT_IDENTIFIERS
    )


def _hostile_digest_segments(folder_id: str) -> tuple[str, ...]:
    return tuple(
        f"{CELERY_TASK_ID}.{folder_id}.{hostile}"
        for hostile in SINGLE_SEGMENT_IDENTIFIERS
    )


@pytest.mark.usefixtures("owned")
@pytest.mark.parametrize("path", STATUS_PATHS)
def test_a_hostile_identifier_is_refused_with_the_task_detail(
    client: TestClient, path: str
) -> None:
    assert answered_details(
        client, path, SINGLE_SEGMENT_IDENTIFIERS, authorization()
    ) == _EXPECTED_REFUSAL


@pytest.mark.parametrize("path", STATUS_PATHS)
def test_a_hostile_task_segment_is_refused(
    client: TestClient, owned: OwnedContent, path: str
) -> None:
    tokens = _hostile_task_segments(owned.folder_id)

    assert answered_details(
        client, path, tokens, authorization()
    ) == _EXPECTED_REFUSAL


@pytest.mark.usefixtures("owned")
@pytest.mark.parametrize("path", STATUS_PATHS)
def test_a_hostile_folder_segment_is_refused(
    client: TestClient, path: str
) -> None:
    tokens = _hostile_folder_segments()

    assert answered_details(
        client, path, tokens, authorization()
    ) == _EXPECTED_REFUSAL


@pytest.mark.parametrize("path", STATUS_PATHS)
def test_a_hostile_digest_segment_is_refused(
    client: TestClient, owned: OwnedContent, path: str
) -> None:
    tokens = _hostile_digest_segments(owned.folder_id)

    assert answered_details(
        client, path, tokens, authorization()
    ) == _EXPECTED_REFUSAL


@pytest.mark.parametrize("path", STATUS_PATHS)
def test_a_mangled_valid_token_is_refused(
    client: TestClient, owned: OwnedContent, path: str
) -> None:
    minted = owned_token(owned.folder_id)
    tokens = (
        minted[:-1],
        minted + "0",
        minted.upper(),
        minted.replace(".", "..", 1),
        f" {minted} ",
        minted + minted,
        minted + "\n",
        "." + minted,
    )

    assert answered_details(
        client, path, tokens, authorization()
    ) == _EXPECTED_REFUSAL


@pytest.mark.parametrize("path", STATUS_PATHS)
def test_no_hostile_token_reaches_a_server_error(
    client: TestClient, owned: OwnedContent, path: str
) -> None:
    tokens = (
        *SINGLE_SEGMENT_IDENTIFIERS,
        *_hostile_folder_segments(),
        *_hostile_digest_segments(owned.folder_id),
    )
    replies = answered_details(client, path, tokens, authorization())
    statuses = {code for code, _detail in replies}

    assert max(statuses) < SERVER_ERROR_FLOOR
    assert replies == _EXPECTED_REFUSAL
