import ast
import inspect
import textwrap
import uuid
from collections.abc import Iterator
from pathlib import Path
from typing import cast
from unittest import mock

import pytest
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from app_factory import create_app
from features.file_upload import file_uploader as uploader_module
from features.file_upload.file_uploader import upload_files
from shared.folder_access import MISSING_FOLDER, owned_folder_id
from shared.models import File as StoredFile
from shared.models import Folder
from tests.access_support import scoped_client
from tests.file_upload_support import (
    FOREIGN_FOLDER_ID,
    NOT_FOUND,
    UNKNOWN_FOLDER_ID,
    names_in,
    refusal_detail,
    sessions_without_a_home_folder,
    storage_directory,
    upload,
)
from tests.support import USER_ID, authorization

_UPLOAD_PATH = "/upload-files"
_HOME = "home"


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    return sessions_without_a_home_folder()


@pytest.fixture
def client(sessions: sessionmaker[Session]) -> Iterator[TestClient]:
    yield from scoped_client(sessions)


def _upload_files_source() -> ast.AsyncFunctionDef:
    source = textwrap.dedent(inspect.getsource(upload_files))

    return cast("ast.AsyncFunctionDef", ast.parse(source).body[0])


def _calls_in(node: ast.AST) -> list[ast.Call]:
    return [
        found for found in ast.walk(node) if isinstance(found, ast.Call)
    ]


def _called_name(call: ast.Call) -> str:
    if isinstance(call.func, ast.Name):
        return call.func.id

    return ""


def _upload_route_dependencies() -> set[object]:
    matching = [
        route
        for route in create_app().routes
        if isinstance(route, APIRoute) and route.path == _UPLOAD_PATH
    ]

    return {
        dependency.call
        for dependency in matching[0].dependant.dependencies
    }


def test_upload_files_resolves_ownership_before_anything_else() -> None:
    first_statement = _upload_files_source().body[0]
    calls = _calls_in(first_statement)
    arguments = [cast("ast.Name", given_) for given_ in calls[0].args]

    assert len(calls) == 1
    assert _called_name(calls[0]) == "owned_folder_id"
    assert [argument.id for argument in arguments] == [
        "db",
        "user_id",
        "folder_id",
    ]


def test_upload_files_does_not_take_ownership_as_a_dependency() -> None:
    called_names = [
        _called_name(call) for call in _calls_in(_upload_files_source())
    ]

    assert owned_folder_id not in _upload_route_dependencies()
    assert "owned_folder_id" in called_names


def test_upload_into_another_learners_folder_is_refused(
    client: TestClient, tmp_path: Path
) -> None:
    with storage_directory(tmp_path):
        response = upload(client, FOREIGN_FOLDER_ID, authorization())

    assert response.status_code == NOT_FOUND
    assert refusal_detail(response) == MISSING_FOLDER


def test_refused_upload_records_no_file_row(
    client: TestClient, sessions: sessionmaker[Session], tmp_path: Path
) -> None:
    with storage_directory(tmp_path):
        _ = upload(client, FOREIGN_FOLDER_ID, authorization())

    with sessions() as session:
        assert session.query(StoredFile).count() == 0


def test_refused_upload_writes_no_bytes(
    client: TestClient, tmp_path: Path
) -> None:
    with storage_directory(tmp_path):
        _ = upload(client, FOREIGN_FOLDER_ID, authorization())

    assert names_in(tmp_path) == set()


def test_upload_without_folder_id_is_refused(
    client: TestClient, tmp_path: Path
) -> None:
    with storage_directory(tmp_path):
        response = upload(client, None, authorization())

    assert response.status_code == NOT_FOUND
    assert refusal_detail(response) == MISSING_FOLDER
    assert names_in(tmp_path) == set()


def test_upload_with_unparsable_folder_id_is_refused(
    client: TestClient, tmp_path: Path
) -> None:
    with storage_directory(tmp_path):
        response = upload(client, "not-a-uuid", authorization())

    assert response.status_code == NOT_FOUND
    assert refusal_detail(response) == MISSING_FOLDER
    assert names_in(tmp_path) == set()


def test_upload_with_unknown_folder_id_is_refused(
    client: TestClient, tmp_path: Path
) -> None:
    with storage_directory(tmp_path):
        response = upload(client, UNKNOWN_FOLDER_ID, authorization())

    assert response.status_code == NOT_FOUND
    assert refusal_detail(response) == MISSING_FOLDER
    assert names_in(tmp_path) == set()


def test_upload_to_home_without_a_home_folder_is_refused(
    client: TestClient, sessions: sessionmaker[Session], tmp_path: Path
) -> None:
    with storage_directory(tmp_path):
        response = upload(client, _HOME, authorization())

    with sessions() as session:
        created_home = session.get(Folder, uuid.UUID(USER_ID))

    assert response.status_code == NOT_FOUND
    assert refusal_detail(response) == MISSING_FOLDER
    assert created_home is None


def test_ownership_refusal_does_not_run_cleanup(
    client: TestClient, tmp_path: Path
) -> None:
    with storage_directory(tmp_path), mock.patch.object(
        uploader_module, "_remove_uploaded_files_from_storage"
    ) as removal:
        response = upload(client, FOREIGN_FOLDER_ID, authorization())

    assert response.status_code == NOT_FOUND
    assert not removal.called
