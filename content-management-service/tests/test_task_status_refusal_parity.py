from collections.abc import Iterator
from typing import Final

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from features.study_units_generation import task_status_router
from features.study_units_generation.task_ownership import (
    MISSING_TASK,
)
from tests.access_support import (
    HOME_ID,
    OTHER_HOME_ID,
    OwnedContent,
    crashless_client,
    seeded_content,
)
from tests.support import (
    OTHER_USER_ID,
    authorization,
    in_memory_sessions,
)
from tests.task_token_support import (
    CELERY_TASK_ID,
    NOT_FOUND,
    STATUS_PATHS,
    RefusingAsyncResult,
    answered,
    forged_token,
    owned_token,
    token_for_an_unknown_folder,
)

_MALFORMED_TASK_REFERENCE: Final[str] = "a.b.zzz"
_REFUSAL_BODY: Final[dict[str, str]] = {"detail": MISSING_TASK}
_REFUSAL: Final[tuple[int, dict[str, str]]] = (
    NOT_FOUND,
    _REFUSAL_BODY,
)
_UNUSABLE_TOKEN_KINDS: Final[int] = 4


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    return in_memory_sessions()


@pytest.fixture
def client(sessions: sessionmaker[Session]) -> Iterator[TestClient]:
    yield from crashless_client(sessions)


@pytest.fixture
def owned(sessions: sessionmaker[Session]) -> OwnedContent:
    return seeded_content(sessions, HOME_ID)


@pytest.fixture
def refusing_celery(
    monkeypatch: pytest.MonkeyPatch,
) -> RefusingAsyncResult:
    celery = RefusingAsyncResult()
    monkeypatch.setattr(task_status_router, "AsyncResult", celery)

    return celery


@pytest.fixture
def stranger(sessions: sessionmaker[Session]) -> dict[str, str]:
    _ = seeded_content(sessions, OTHER_HOME_ID)

    return authorization(OTHER_USER_ID)


def _unusable_tokens(folder_id: str) -> tuple[str, ...]:
    return (
        forged_token(folder_id),
        token_for_an_unknown_folder(),
        _MALFORMED_TASK_REFERENCE,
        CELERY_TASK_ID,
    )


@pytest.mark.usefixtures("refusing_celery")
@pytest.mark.parametrize("path", STATUS_PATHS)
def test_every_rejection_is_the_same_404_body(
    client: TestClient, owned: OwnedContent, path: str
) -> None:
    answers = [
        answered(client, path, token, authorization())
        for token in _unusable_tokens(owned.folder_id)
    ]

    assert len(answers) == _UNUSABLE_TOKEN_KINDS
    assert answers == [_REFUSAL] * _UNUSABLE_TOKEN_KINDS


@pytest.mark.usefixtures("refusing_celery")
@pytest.mark.parametrize("path", STATUS_PATHS)
def test_another_users_well_signed_token_joins_the_same_404(
    client: TestClient,
    owned: OwnedContent,
    stranger: dict[str, str],
    path: str,
) -> None:
    reply = answered(
        client, path, owned_token(owned.folder_id), stranger
    )

    assert reply == _REFUSAL


@pytest.mark.usefixtures("owned", "refusing_celery")
@pytest.mark.parametrize("path", STATUS_PATHS)
def test_a_raw_celery_identifier_is_no_longer_accepted(
    client: TestClient, path: str
) -> None:
    reply = answered(client, path, CELERY_TASK_ID, authorization())

    assert reply == _REFUSAL
