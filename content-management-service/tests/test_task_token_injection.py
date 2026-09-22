from collections.abc import Iterator
from typing import Final, override
from unittest import mock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from app_factory import create_app
from features.study_units_generation import (
    generation_router,
    task_status_router,
)
from features.study_units_generation.task_ownership import (
    SecretSignedTaskTokens,
)
from features.study_units_generation.task_token_contracts import (
    TaskTokenSigner,
    TaskTokenVerifier,
)
from shared.database import get_db
from tests.access_support import HOME_ID, OwnedContent, seeded_content
from tests.property_fakes import RecordingQueuedTask
from tests.support import SessionProvider, authorization, in_memory_sessions
from tests.task_token_support import (
    CELERY_TASK_ID,
    NOTE_TASK_STATUS,
    OK,
    PENDING,
    TASK_TOKENS,
    PendingAsyncResult,
)

_READABLE_SEPARATOR: Final[str] = "~"
_QUEUED_NOTE_ID: Final[str] = "note-1"


class ReadableTaskTokens(TaskTokenSigner, TaskTokenVerifier):
    @override
    def signed_task_id(self, task_id: str, folder_id: str) -> str:
        return f"{task_id}{_READABLE_SEPARATOR}{folder_id}"

    @override
    def verified_task_id(self, token: str) -> tuple[str, str]:
        task_id, _, folder_id = token.partition(_READABLE_SEPARATOR)

        return task_id, folder_id


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    return in_memory_sessions()


@pytest.fixture
def owned(sessions: sessionmaker[Session]) -> OwnedContent:
    return seeded_content(sessions, HOME_ID)


@pytest.fixture
def client(sessions: sessionmaker[Session]) -> Iterator[TestClient]:
    app = create_app()
    app.dependency_overrides[get_db] = SessionProvider(sessions)
    app.dependency_overrides[SecretSignedTaskTokens] = ReadableTaskTokens

    with TestClient(app) as test_client:
        yield test_client


def test_secret_signed_task_tokens_fulfil_both_contracts() -> None:
    assert isinstance(TASK_TOKENS, TaskTokenSigner)
    assert isinstance(TASK_TOKENS, TaskTokenVerifier)


def test_generation_signs_with_the_injected_signer(
    client: TestClient, owned: OwnedContent
) -> None:
    queued_note = RecordingQueuedTask(_QUEUED_NOTE_ID)
    requested: dict[str, object] = {
        "text": "material",
        "folder_id": owned.folder_id,
        "note": {},
    }

    with mock.patch.object(
        generation_router, "generate_note_task", queued_note
    ):
        response = client.post(
            "/generate-study-units", json=requested, headers=authorization()
        )

    expected_token = f"{_QUEUED_NOTE_ID}{_READABLE_SEPARATOR}{owned.folder_id}"

    assert response.status_code == OK
    assert response.json() == {"note_task_id": expected_token}


def test_status_reads_the_token_with_the_injected_verifier(
    client: TestClient,
    owned: OwnedContent,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    celery = PendingAsyncResult()
    monkeypatch.setattr(task_status_router, "AsyncResult", celery)
    token = f"{CELERY_TASK_ID}{_READABLE_SEPARATOR}{owned.folder_id}"

    response = client.get(
        f"{NOTE_TASK_STATUS}/{token}", headers=authorization()
    )

    assert response.status_code == OK
    assert response.json() == {"status": PENDING}
    assert celery.looked_up == [CELERY_TASK_ID]
