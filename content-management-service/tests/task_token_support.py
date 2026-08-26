import uuid
from typing import Final, cast
from urllib.parse import quote

from fastapi.testclient import TestClient

from features.study_units_generation.task_ownership import signed_task_id

FLASHCARDS_STATUS: Final[str] = "/flashcards-status"
TEST_TASK_STATUS: Final[str] = "/test-task-status"
NOTE_TASK_STATUS: Final[str] = "/note-task-status"

STATUS_PATHS: Final[tuple[str, str, str]] = (
    FLASHCARDS_STATUS,
    TEST_TASK_STATUS,
    NOTE_TASK_STATUS,
)

CELERY_TASK_ID: Final[str] = "b7c0e1f2-0000-4000-8000-00000000ab01"
FORGED_DIGEST: Final[str] = "0" * 64
DIGEST_LENGTH: Final[int] = 64
NOT_FOUND: Final[int] = 404
UNAUTHORIZED: Final[int] = 401
OK: Final[int] = 200
SERVER_ERROR_FLOOR: Final[int] = 500
PENDING: Final[str] = "PENDING"


def owned_token(folder_id: str) -> str:
    return signed_task_id(CELERY_TASK_ID, folder_id)


def forged_token(folder_id: str) -> str:
    return f"{CELERY_TASK_ID}.{folder_id}.{FORGED_DIGEST}"


def token_for_an_unknown_folder() -> str:
    return signed_task_id(CELERY_TASK_ID, str(uuid.uuid4()))


class ForbiddenCeleryLookupError(AssertionError):
    def __init__(self) -> None:
        super().__init__("a refused token reached Celery")


class RefusingAsyncResult:
    def __call__(self, task_id: str, app: object = None) -> object:
        _ = task_id
        _ = app

        raise ForbiddenCeleryLookupError


class PendingAsyncResult:
    def __init__(self) -> None:
        self.looked_up: list[str] = []
        self.status: str = PENDING
        self.result: object = None

    def __call__(
        self, task_id: str, app: object = None
    ) -> "PendingAsyncResult":
        _ = app
        self.looked_up.append(task_id)

        return self

    def ready(self) -> bool:
        return False


class SucceededAsyncResult:
    def __init__(self, finished: dict[str, object]) -> None:
        self.looked_up: list[str] = []
        self.status: str = "SUCCESS"
        self.result: dict[str, object] = finished

    def __call__(
        self, task_id: str, app: object = None
    ) -> "SucceededAsyncResult":
        _ = app
        self.looked_up.append(task_id)

        return self

    def ready(self) -> bool:
        return True


def answered(
    client: TestClient, path: str, token: str, headers: dict[str, str]
) -> tuple[int, dict[str, object]]:
    response = client.get(f"{path}/{token}", headers=headers)

    return response.status_code, cast(
        "dict[str, object]", response.json()
    )


def answered_details(
    client: TestClient,
    path: str,
    tokens: tuple[str, ...],
    headers: dict[str, str],
) -> set[tuple[int, str]]:
    replies: set[tuple[int, str]] = set()

    for token in tokens:
        code, body = answered(
            client, path, quote(token, safe=""), headers
        )
        replies.add((code, str(body.get("detail"))))

    return replies
