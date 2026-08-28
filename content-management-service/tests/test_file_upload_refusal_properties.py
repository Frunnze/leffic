import tempfile
import uuid
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from hypothesis import given, settings
from hypothesis import strategies as st
from sqlalchemy.orm import Session, sessionmaker

from shared.folder_access import MISSING_FOLDER
from shared.models import Folder
from tests.access_support import scoped_client
from tests.file_upload_support import (
    FOREIGN_FOLDER_ID,
    LEARNER_FOLDER_ID,
    NOT_FOUND,
    names_in,
    refusal_detail,
    sessions_without_a_home_folder,
    storage_directory,
    upload,
)
from tests.folder_seeding import seeded_folder
from tests.hostile_identifiers import HOSTILE_IDENTIFIERS
from tests.property_support import property_world
from tests.support import OTHER_USER_ID, authorization

_HOME = "home"
_PRINTABLE = st.characters(min_codepoint=33, max_codepoint=126)
_HOSTILE_FILENAMES = (
    "\u00fcn\u00efc\u00f8d\u00e9.pdf",
    "\U0001f648.pdf",
    "x" * 200 + ".pdf",
    " .pdf",
    "no-extension",
)
_PROPERTY_CLIENT, _PROPERTY_SESSIONS = property_world()
_PROPERTY_STORAGE = Path(tempfile.mkdtemp())


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    return sessions_without_a_home_folder()


@pytest.fixture
def client(sessions: sessionmaker[Session]) -> Iterator[TestClient]:
    yield from scoped_client(sessions)


def _is_not_a_uuid(text: str) -> bool:
    try:
        _ = uuid.UUID(text)
    except ValueError:
        return True

    return False


def test_upload_to_home_ignores_another_learners_home_folder(
    client: TestClient, sessions: sessionmaker[Session], tmp_path: Path
) -> None:
    with sessions() as session:
        session.add(
            Folder(
                id=uuid.UUID(OTHER_USER_ID),
                name="Home",
                user_id=uuid.UUID(OTHER_USER_ID),
            )
        )
        session.commit()

    with storage_directory(tmp_path):
        response = upload(client, _HOME, authorization())

    assert response.status_code == NOT_FOUND
    assert names_in(tmp_path) == set()


@pytest.mark.parametrize("folder_id", HOSTILE_IDENTIFIERS)
def test_a_hostile_folder_id_is_refused_as_a_missing_folder(
    client: TestClient, tmp_path: Path, folder_id: str
) -> None:
    with storage_directory(tmp_path):
        response = upload(client, folder_id, authorization())

    assert response.status_code == NOT_FOUND
    assert refusal_detail(response) == MISSING_FOLDER


@pytest.mark.parametrize("folder_id", HOSTILE_IDENTIFIERS)
def test_a_hostile_folder_id_leaves_the_storage_directory_empty(
    client: TestClient, tmp_path: Path, folder_id: str
) -> None:
    with storage_directory(tmp_path):
        _ = upload(client, folder_id, authorization())

    assert names_in(tmp_path) == set()


@pytest.mark.parametrize("filename", _HOSTILE_FILENAMES)
def test_a_refused_upload_of_a_hostile_filename_writes_nothing(
    client: TestClient, tmp_path: Path, filename: str
) -> None:
    with storage_directory(tmp_path):
        response = upload(
            client, FOREIGN_FOLDER_ID, authorization(), (filename,)
        )

    assert response.status_code == NOT_FOUND
    assert names_in(tmp_path) == set()


def test_a_refused_upload_of_many_files_writes_none_of_them(
    client: TestClient, tmp_path: Path
) -> None:
    with storage_directory(tmp_path):
        response = upload(
            client,
            FOREIGN_FOLDER_ID,
            authorization(),
            _HOSTILE_FILENAMES,
        )

    assert response.status_code == NOT_FOUND
    assert names_in(tmp_path) == set()


def test_an_upload_from_another_learner_into_an_owned_folder_is_refused(
    client: TestClient, tmp_path: Path
) -> None:
    with storage_directory(tmp_path):
        response = upload(
            client, LEARNER_FOLDER_ID, authorization(OTHER_USER_ID)
        )

    assert response.status_code == NOT_FOUND
    assert refusal_detail(response) == MISSING_FOLDER
    assert names_in(tmp_path) == set()


@settings(max_examples=25, deadline=None)
@given(st.uuids())
def test_upload_files_property_refuses_every_folder_owned_by_another(
    owner: uuid.UUID,
) -> None:
    with _PROPERTY_SESSIONS() as session:
        folder_id = seeded_folder(session, owner, {})

    with storage_directory(_PROPERTY_STORAGE):
        response = upload(
            _PROPERTY_CLIENT, str(folder_id), authorization()
        )

    assert response.status_code == NOT_FOUND
    assert refusal_detail(response) == MISSING_FOLDER


@settings(max_examples=25, deadline=None)
@given(st.uuids())
def test_upload_files_property_writes_no_bytes_for_an_unknown_folder(
    absent: uuid.UUID,
) -> None:
    with storage_directory(_PROPERTY_STORAGE):
        before = names_in(_PROPERTY_STORAGE)
        response = upload(_PROPERTY_CLIENT, str(absent), authorization())

    assert response.status_code == NOT_FOUND
    assert names_in(_PROPERTY_STORAGE) == before


@settings(max_examples=25, deadline=None)
@given(st.text(alphabet=_PRINTABLE, min_size=1).filter(_is_not_a_uuid))
def test_upload_files_property_refuses_every_unparsable_folder_id(
    folder_id: str,
) -> None:
    with storage_directory(_PROPERTY_STORAGE):
        before = names_in(_PROPERTY_STORAGE)
        response = upload(_PROPERTY_CLIENT, folder_id, authorization())

    assert response.status_code == NOT_FOUND
    assert refusal_detail(response) == MISSING_FOLDER
    assert names_in(_PROPERTY_STORAGE) == before

