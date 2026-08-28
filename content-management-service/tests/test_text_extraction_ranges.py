from collections.abc import Iterator
from pathlib import Path
from typing import cast
from unittest import mock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from features.study_units_generation import (
    extraction_router as router_module,
)
from features.study_units_generation.text_sources import StoredDocument
from tests.access_support import scoped_client
from tests.extraction_support import OK, extract, stored_file_id
from tests.support import USER_ID, authorization, in_memory_sessions

_PAGE_TEXT = "A neuron at rest sits near -70 mV."


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    return in_memory_sessions()


@pytest.fixture
def client(sessions: sessionmaker[Session]) -> Iterator[TestClient]:
    yield from scoped_client(sessions)


def _requested_pages(
    client: TestClient, file_id: str, asked: dict[str, int]
) -> tuple[int, StoredDocument]:
    payload: dict[str, object] = {
        "file_metadata": [{"file_id": file_id, "pages": asked}]
    }

    with mock.patch.object(
        router_module, "text_from_files", return_value=_PAGE_TEXT
    ) as from_files:
        code, _ = extract(client, payload, authorization(USER_ID))

    requested = cast(
        "list[StoredDocument]", from_files.call_args.args[0]
    )

    return code, requested[0]


def test_a_range_without_an_end_reads_on_to_the_last_page(
    client: TestClient, sessions: sessionmaker[Session], tmp_path: Path
) -> None:
    file_id = stored_file_id(sessions, USER_ID, tmp_path)

    code, document = _requested_pages(client, file_id, {"first": 2})

    assert code == OK
    assert document.pages is not None
    assert document.pages.last is None


def test_a_range_without_a_start_begins_at_the_first_page(
    client: TestClient, sessions: sessionmaker[Session], tmp_path: Path
) -> None:
    file_id = stored_file_id(sessions, USER_ID, tmp_path)

    code, document = _requested_pages(client, file_id, {"last": 3})

    assert code == OK
    assert document.pages is not None
    assert document.pages.first == 1
