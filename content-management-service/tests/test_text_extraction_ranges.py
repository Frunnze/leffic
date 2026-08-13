from collections.abc import Iterator
from typing import TYPE_CHECKING, cast
from unittest import mock

import jwt
import pytest
from fastapi.testclient import TestClient

from app_factory import create_app
from features.study_units_generation import (
    extraction_router as router_module,
)

if TYPE_CHECKING:
    from features.study_units_generation.text_sources import (
        FileMetadata,
    )

_USER_ID = "6f1c7d4e-0000-4000-8000-000000000001"
_PAGE_TEXT = "A neuron at rest sits near -70 mV."


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(create_app()) as test_client:
        yield test_client


def _authorization() -> dict[str, str]:
    token = jwt.encode({"user_id": _USER_ID}, "secret", algorithm="HS256")

    return {"Authorization": f"Bearer {token}"}


def _extract(
    client: TestClient, payload: dict[str, object]
) -> tuple[int, dict[str, object]]:
    response = client.post(
        "/extract-text", json=payload, headers=_authorization()
    )

    return response.status_code, cast("dict[str, object]", response.json())


def test_a_range_without_an_end_reads_on_to_the_last_page(
    client: TestClient,
) -> None:
    with mock.patch.object(
        router_module, "text_from_files", return_value=_PAGE_TEXT
    ) as from_files:
        code, _ = _extract(
            client,
            {
                "file_metadata": [
                    {
                        "file_id": "f1",
                        "extension": "pdf",
                        "pages": {"first": 2},
                    }
                ]
            },
        )

    requested = cast("list[FileMetadata]", from_files.call_args.args[0])

    assert code == 200
    assert requested[0].pages is not None
    assert requested[0].pages.last is None


def test_a_range_without_a_start_begins_at_the_first_page(
    client: TestClient,
) -> None:
    with mock.patch.object(
        router_module, "text_from_files", return_value=_PAGE_TEXT
    ) as from_files:
        code, _ = _extract(
            client,
            {
                "file_metadata": [
                    {
                        "file_id": "f1",
                        "extension": "pdf",
                        "pages": {"last": 3},
                    }
                ]
            },
        )

    requested = cast("list[FileMetadata]", from_files.call_args.args[0])

    assert code == 200
    assert requested[0].pages is not None
    assert requested[0].pages.first == 1
