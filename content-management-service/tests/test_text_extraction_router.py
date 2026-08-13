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
from features.study_units_generation.pdf_pages import PageSelectionError

if TYPE_CHECKING:
    from features.study_units_generation.text_sources import (
        FileMetadata,
    )

_USER_ID = "6f1c7d4e-0000-4000-8000-000000000001"
_PAGE_TEXT = "A neuron at rest sits near -70 mV."
_TOO_FEW_PAGES = "The document has only 4 pages"


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


def test_a_topic_is_not_extracted_but_written_into_a_note(
    client: TestClient,
) -> None:
    code, body = _extract(client, {"topic_metadata": "photosynthesis"})

    assert code == 400
    assert body["msg"] == "A topic is written into a note, not extracted."


def test_a_link_is_read_into_text(client: TestClient) -> None:
    with mock.patch.object(
        router_module, "text_from_link", return_value=_PAGE_TEXT
    ) as from_link:
        code, body = _extract(
            client, {"link_metadata": "https://example.com/neurons"}
        )

    assert code == 200
    assert body == {"text": _PAGE_TEXT}
    assert from_link.call_args.args[0] == "https://example.com/neurons"


def test_a_file_is_read_into_text(client: TestClient) -> None:
    with mock.patch.object(
        router_module, "text_from_files", return_value=_PAGE_TEXT
    ) as from_files:
        code, body = _extract(
            client,
            {
                "file_metadata": [
                    {
                        "file_id": "6f1c7d4e-0000-4000-8000-00000000000a",
                        "name": "action-potentials.pdf",
                        "extension": "pdf",
                    }
                ]
            },
        )

    assert code == 200
    assert body == {"text": _PAGE_TEXT}
    requested = cast("list[FileMetadata]", from_files.call_args.args[0])

    assert requested[0].file_id == "6f1c7d4e-0000-4000-8000-00000000000a"


def test_a_source_that_yields_nothing_is_rejected(
    client: TestClient,
) -> None:
    code, _ = _extract(client, {})

    assert code == 400


def test_extraction_needs_a_token(client: TestClient) -> None:
    response = client.post(
        "/extract-text", json={"topic_metadata": "photosynthesis"}
    )

    assert response.status_code == 401


def test_a_page_range_that_the_document_cannot_serve_is_refused(
    client: TestClient,
) -> None:
    with mock.patch.object(
        router_module,
        "text_from_files",
        mock.Mock(side_effect=PageSelectionError(_TOO_FEW_PAGES)),
    ):
        response = client.post(
            "/extract-text",
            json={
                "file_metadata": [
                    {
                        "file_id": "f1",
                        "extension": "pdf",
                        "pages": {"first": 9, "last": 12},
                    }
                ]
            },
            headers=_authorization(),
        )

    assert response.status_code == 400
    assert cast("dict[str, str]", response.json())["msg"] == _TOO_FEW_PAGES


def test_a_backwards_page_range_is_rejected(client: TestClient) -> None:
    response = client.post(
        "/extract-text",
        json={
            "file_metadata": [
                {
                    "file_id": "f1",
                    "extension": "pdf",
                    "pages": {"first": 8, "last": 3},
                }
            ]
        },
        headers=_authorization(),
    )

    assert response.status_code == 422
