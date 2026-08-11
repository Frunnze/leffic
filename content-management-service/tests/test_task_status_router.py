from collections.abc import Iterator
from typing import cast
from unittest import mock

import pytest
from fastapi.testclient import TestClient

from app_factory import create_app
from features.study_units_generation import task_status_router
from shared.celery_app import celery_app

_USER_ID = "6f1c7d4e-0000-4000-8000-000000000001"
_FOLDER_ID = "6f1c7d4e-0000-4000-8000-000000000002"


class FakeTaskResult:
    def __init__(self, task_id: str) -> None:
        super().__init__()
        self.id: str = task_id


class FakeTask:
    def __init__(self, task_id: str) -> None:
        super().__init__()
        self.task_id: str = task_id
        self.calls: list[dict[str, object]] = []

    def delay(self, **kwargs: object) -> FakeTaskResult:
        self.calls.append(kwargs)

        return FakeTaskResult(self.task_id)


class FakeAsyncResult:
    def __init__(self, status: str, result: object | None) -> None:
        super().__init__()
        self.status: str = status
        self.result: object | None = result

    def ready(self) -> bool:
        return self.result is not None


class FakeAi:
    def get_ai_res_hist(
        self, system_prompt: str, history: list[object]
    ) -> str:
        return f"answered {len(history)} messages for {len(system_prompt)}"


class FakeFactory:
    def __init__(self) -> None:
        super().__init__()
        self.models: list[str | None] = []

    def get_ai(self, model: str | None = None) -> FakeAi:
        self.models.append(model)

        return FakeAi()


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(create_app()) as test_client:
        yield test_client


@pytest.mark.parametrize(
    ("path", "stored", "expected_key"),
    [
        (
            "/flashcards-status",
            {"flashcard_deck_id": "d1"},
            "flashcard_deck_id",
        ),
        ("/test-task-status", {"test_id": "t1"}, "test_id"),
        ("/note-task-status", {"note_id": "n1"}, "note_id"),
    ],
)
def test_a_finished_task_reports_its_study_unit(
    client: TestClient,
    path: str,
    stored: dict[str, object],
    expected_key: str,
) -> None:
    with mock.patch.object(
        task_status_router,
        "AsyncResult",
        return_value=FakeAsyncResult("SUCCESS", stored),
    ) as looked_up:
        response = client.get(f"{path}/task-1")

    body = cast("dict[str, object]", response.json())

    assert body[expected_key] == stored[expected_key]
    assert body["status"] == "SUCCESS"
    assert looked_up.call_args.args[0] == "task-1"
    assert looked_up.call_args.kwargs["app"] is celery_app


@pytest.mark.parametrize(
    "path",
    ["/flashcards-status", "/test-task-status", "/note-task-status"],
)
def test_a_pending_task_reports_only_its_status(
    client: TestClient, path: str
) -> None:
    with mock.patch.object(
        task_status_router,
        "AsyncResult",
        return_value=FakeAsyncResult("PENDING", None),
    ):
        response = client.get(f"{path}/task-1")

    assert response.json() == {"status": "PENDING"}


def test_an_unfinished_result_object_is_rejected(
    client: TestClient,
) -> None:
    with (
        mock.patch.object(
            task_status_router,
            "AsyncResult",
            return_value=FakeAsyncResult("SUCCESS", ["not", "a", "dict"]),
        ),
        pytest.raises(TypeError, match="did not finish with a result"),
    ):
        _ = client.get("/note-task-status/task-1")


@pytest.mark.parametrize(
    "path",
    ["/flashcards-status", "/test-task-status", "/note-task-status"],
)
def test_a_failed_task_reports_its_failure(
    client: TestClient, path: str
) -> None:
    with mock.patch.object(
        task_status_router,
        "AsyncResult",
        return_value=FakeAsyncResult("FAILURE", RuntimeError("no folder")),
    ):
        response = client.get(f"{path}/task-1")

    assert response.status_code == 200
    assert response.json() == {"status": "FAILURE"}
