import uuid
from collections.abc import Iterator
from pathlib import Path
from unittest import mock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from src.app_factory import create_app
from src.features.file_system import file_storage
from src.features.file_system.file_storage import delete_file_from_storage
from src.shared.database import get_db
from src.shared.models import (
    File,
    Folder,
)
from tests.support import (
    USER_ID,
    SessionProvider,
    in_memory_sessions,
)

_HOME_ID = uuid.UUID(USER_ID)


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    return in_memory_sessions()


@pytest.fixture
def client(sessions: sessionmaker[Session]) -> Iterator[TestClient]:
    app = create_app()
    app.dependency_overrides[get_db] = SessionProvider(sessions)

    with TestClient(app) as test_client:
        yield test_client


def _home_folder(session: Session) -> Folder:
    folder = Folder(id=_HOME_ID, name="Home", user_id=_HOME_ID)
    session.add(folder)
    session.commit()

    return folder


def test_deleting_a_folder_removes_its_files(
    client: TestClient, sessions: sessionmaker[Session], tmp_path: Path
) -> None:
    with sessions() as session:
        folder = _home_folder(session)
        stored = File(folder_id=folder.id, name="doc", extension="pdf")
        session.add(stored)
        session.commit()
        stored_name = f"{stored.id}.pdf"

    _ = (tmp_path / stored_name).write_bytes(b"payload")

    with mock.patch.object(file_storage, "_FILES_DIRECTORY", str(tmp_path)):
        response = client.request(
            "DELETE", "/delete-folder/", params={"folder_id": str(_HOME_ID)}
        )

    assert response.json() == {"msg": "Folder deleted!"}
    assert not (tmp_path / stored_name).exists()


def test_deleting_a_missing_file_from_storage_is_harmless(
    tmp_path: Path,
) -> None:
    with mock.patch.object(file_storage, "_FILES_DIRECTORY", str(tmp_path)):
        delete_file_from_storage("absent.pdf")
