import inspect
import tempfile
import uuid
from collections.abc import Iterator
from pathlib import Path
from typing import cast
from unittest import mock

import pytest
from fastapi.testclient import TestClient
from hypothesis import given, settings
from hypothesis import strategies as st
from sqlalchemy.orm import Session, sessionmaker

from features.file_upload import file_uploader as uploader_module
from features.file_upload.file_uploader import (
    _recorded_files,
    save_file_to_storage,
)
from shared.models import File as StoredFile
from tests.access_support import scoped_client
from tests.file_upload_support import (
    EXTENSIONS,
    LEARNER_FOLDER_ID,
    OK,
    UNKNOWN_FOLDER_ID,
    an_upload,
    numbered_filenames,
    sessions_without_a_home_folder,
    storage_directory,
    upload,
    uploaded_metadata,
)
from tests.folder_seeding import seeded_folder
from tests.property_support import property_world
from tests.support import USER_ID, authorization

_PROPERTY_CLIENT, _PROPERTY_SESSIONS = property_world()
_PROPERTY_STORAGE = Path(tempfile.mkdtemp())


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    return sessions_without_a_home_folder()


@pytest.fixture
def client(sessions: sessionmaker[Session]) -> Iterator[TestClient]:
    yield from scoped_client(sessions)


def test_an_owned_folder_still_accepts_the_upload(
    client: TestClient, sessions: sessionmaker[Session], tmp_path: Path
) -> None:
    with storage_directory(tmp_path):
        response = upload(client, LEARNER_FOLDER_ID, authorization())

    stored = uploaded_metadata(response)[0]

    with sessions() as session:
        recorded = session.query(StoredFile).one()

    assert response.status_code == OK
    assert stored["name"] == "notes.pdf"
    assert str(recorded.folder_id) == LEARNER_FOLDER_ID


def test__recorded_files_keeps_its_signature() -> None:
    signature = inspect.signature(_recorded_files)
    annotated = {
        name: cast("object", parameter.annotation)
        for name, parameter in signature.parameters.items()
    }

    assert list(annotated) == ["db", "folder_id", "uploaded_files"]
    assert annotated["db"] is Session
    assert annotated["folder_id"] is str
    assert annotated["uploaded_files"] == list[dict[str, str]]
    assert cast("object", signature.return_annotation) is None


def test__recorded_files_does_not_check_the_folder(
    sessions: sessionmaker[Session],
) -> None:
    with sessions() as session:
        recorded = _recorded_files(session, UNKNOWN_FOLDER_ID, [])

    assert recorded is None


def test__recorded_files_adds_rows_in_one_batch(
    sessions: sessionmaker[Session],
) -> None:
    uploaded = [
        {
            "file_id": str(uuid.uuid4()),
            "extension": "pdf",
            "name": "notes.pdf",
        }
    ]

    with sessions() as session, mock.patch.object(
        Session, "add_all"
    ) as add_all, mock.patch.object(Session, "commit") as commit:
        _recorded_files(session, LEARNER_FOLDER_ID, uploaded)

    assert add_all.call_count == 1

    added = cast("list[StoredFile]", add_all.call_args.args[0])

    assert [str(row.id) for row in added] == [uploaded[0]["file_id"]]
    assert [str(row.folder_id) for row in added] == [LEARNER_FOLDER_ID]
    assert [row.name for row in added] == ["notes.pdf"]
    assert commit.called


def test_dead_folder_constants_are_gone() -> None:
    assert not hasattr(uploader_module, "_HOME_FOLDER")
    assert not hasattr(uploader_module, "_MISSING_FOLDER")
    assert not hasattr(uploader_module, "Folder")


def test_save_file_to_storage_does_not_create_the_directory(
    tmp_path: Path,
) -> None:
    absent = tmp_path / "files"

    with storage_directory(absent), pytest.raises(FileNotFoundError):
        save_file_to_storage(an_upload("notes.pdf", b"payload"), "a.pdf")

    assert not absent.exists()


@settings(max_examples=25, deadline=None)
@given(st.uuids())
def test__recorded_files_property_never_refuses_the_folder_it_is_given(
    absent: uuid.UUID,
) -> None:
    with _PROPERTY_SESSIONS() as session:
        recorded = _recorded_files(session, str(absent), [])

    assert recorded is None


@settings(max_examples=25, deadline=None)
@given(st.integers(min_value=1, max_value=4), EXTENSIONS)
def test_upload_files_property_answers_for_every_owned_upload(
    file_count: int, extension: str
) -> None:
    with _PROPERTY_SESSIONS() as session:
        folder_id = seeded_folder(session, uuid.UUID(USER_ID), {})

    filenames = numbered_filenames(file_count, extension)

    with storage_directory(_PROPERTY_STORAGE):
        response = upload(
            _PROPERTY_CLIENT, str(folder_id), authorization(), filenames
        )

    described = uploaded_metadata(response)

    assert response.status_code == OK
    assert [item["name"] for item in described] == list(filenames)
