from collections.abc import Iterator
from typing import Final

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app_factory import create_app
from features.study_units_generation import task_status_router
from features.study_units_generation.task_ownership import MISSING_TASK
from shared.database import get_db
from tests.support import authorization
from tests.task_token_support import (
    NOT_FOUND,
    STATUS_PATHS,
    RefusingAsyncResult,
    answered,
    forged_token,
)

_FOLDER_ID: Final[str] = "6f1c7d4e-0000-4000-8000-0000000000c1"
_REFUSAL: Final[tuple[int, dict[str, str]]] = (
    NOT_FOUND,
    {"detail": MISSING_TASK},
)


class ForbiddenDatabaseWorkError(AssertionError):
    def __init__(self) -> None:
        super().__init__("a refused token reached the database")


class RefusingSession:
    def query(self, *models: object) -> object:
        _ = models

        raise ForbiddenDatabaseWorkError

    def execute(self, *statement: object) -> object:
        _ = statement

        raise ForbiddenDatabaseWorkError


class RefusingSessionProvider:
    def __init__(self) -> None:
        self.session: RefusingSession = RefusingSession()

    def __call__(self) -> RefusingSession:
        return self.session


def _wired_app() -> FastAPI:
    app = create_app()
    app.dependency_overrides[get_db] = RefusingSessionProvider()

    return app


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(_wired_app()) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def refusing_celery(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        task_status_router, "AsyncResult", RefusingAsyncResult()
    )


@pytest.mark.parametrize("path", STATUS_PATHS)
def test_a_forged_signature_is_refused_before_any_database_work(
    client: TestClient, path: str
) -> None:
    reply = answered(
        client, path, forged_token(_FOLDER_ID), authorization()
    )

    assert reply == _REFUSAL
