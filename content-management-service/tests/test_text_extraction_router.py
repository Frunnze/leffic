from collections.abc import Iterator
from pathlib import Path
from typing import TYPE_CHECKING, cast
from unittest import mock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from features.study_units_generation import (
    extraction_router as router_module,
)
from features.study_units_generation.pdf_pages import PageSelectionError
from tests.access_support import scoped_client
from tests.extraction_support import (
    BAD_REQUEST,
    DOCUMENT_TEXT,
    NO_TEXT,
    OK,
    STORED_EXTENSION,
    TOPIC_IS_WRITTEN,
    extract,
    extraction_world,
    file_entries,
    stored_file_id,
)
from tests.support import USER_ID, authorization, in_memory_sessions

_PAGE_TEXT = "A neuron at rest sits near -70 mV."
_TOO_FEW_PAGES = "The document has only 4 pages"
_UNAUTHORIZED = 401
_UNPROCESSABLE_ENTITY = 422
_LINK = "https://example.com/neurons"

if TYPE_CHECKING:
    from features.study_units_generation.text_sources import (
        StoredDocument,
    )


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    return in_memory_sessions()


@pytest.fixture
def client(sessions: sessionmaker[Session]) -> Iterator[TestClient]:
    yield from scoped_client(sessions)


def test_a_topic_is_not_extracted_but_written_into_a_note(
    client: TestClient,
) -> None:
    code, body = extract(
        client, {"topic_metadata": "photosynthesis"}, authorization(USER_ID)
    )

    assert code == BAD_REQUEST
    assert body == {"msg": TOPIC_IS_WRITTEN}


def test_a_link_is_read_into_text(client: TestClient) -> None:
    with mock.patch.object(
        router_module, "text_from_link", return_value=_PAGE_TEXT
    ) as from_link:
        code, body = extract(
            client, {"link_metadata": _LINK}, authorization(USER_ID)
        )

    assert code == OK
    assert body == {"text": _PAGE_TEXT}
    assert from_link.call_args.args[0] == _LINK


def test_a_file_is_read_into_text(
    client: TestClient, sessions: sessionmaker[Session], tmp_path: Path
) -> None:
    file_id = stored_file_id(sessions, USER_ID, tmp_path)

    with mock.patch.object(
        router_module, "text_from_files", return_value=_PAGE_TEXT
    ) as from_files:
        code, body = extract(
            client, file_entries(file_id), authorization(USER_ID)
        )

    requested = cast(
        "list[StoredDocument]", from_files.call_args.args[0]
    )

    assert code == OK
    assert body == {"text": _PAGE_TEXT}
    assert requested[0].storage_name == f"{file_id}.{STORED_EXTENSION}"


def test_success_body_is_unchanged(
    client: TestClient, sessions: sessionmaker[Session], tmp_path: Path
) -> None:
    file_id = stored_file_id(sessions, USER_ID, tmp_path)

    with extraction_world(tmp_path):
        code, body = extract(
            client, file_entries(file_id), authorization(USER_ID)
        )

    assert code == OK
    assert body == {"text": DOCUMENT_TEXT}


def test_empty_file_metadata_is_400(client: TestClient) -> None:
    code, body = extract(
        client, {"file_metadata": []}, authorization(USER_ID)
    )

    assert code == BAD_REQUEST
    assert body == {"msg": NO_TEXT}


def test_a_source_that_yields_nothing_is_rejected(
    client: TestClient,
) -> None:
    code, body = extract(client, {}, authorization(USER_ID))

    assert code == BAD_REQUEST
    assert body == {"msg": NO_TEXT}


def test_extraction_needs_a_token(client: TestClient) -> None:
    response = client.post(
        "/extract-text", json={"topic_metadata": "photosynthesis"}
    )

    assert response.status_code == _UNAUTHORIZED


def test_a_page_range_that_the_document_cannot_serve_is_refused(
    client: TestClient, sessions: sessionmaker[Session], tmp_path: Path
) -> None:
    file_id = stored_file_id(sessions, USER_ID, tmp_path)
    payload: dict[str, object] = {
        "file_metadata": [
            {"file_id": file_id, "pages": {"first": 9, "last": 12}}
        ]
    }

    with mock.patch.object(
        router_module,
        "text_from_files",
        mock.Mock(side_effect=PageSelectionError(_TOO_FEW_PAGES)),
    ):
        code, body = extract(client, payload, authorization(USER_ID))

    assert code == BAD_REQUEST
    assert body == {"msg": _TOO_FEW_PAGES}


def test_a_backwards_page_range_is_rejected(client: TestClient) -> None:
    payload = {
        "file_metadata": [
            {"file_id": "f1", "pages": {"first": 8, "last": 3}}
        ]
    }
    response = client.post(
        "/extract-text", json=payload, headers=authorization(USER_ID)
    )

    assert response.status_code == _UNPROCESSABLE_ENTITY
