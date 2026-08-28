from collections.abc import Iterator
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from features.file_upload import file_uploader as uploader_module
from tests.access_support import scoped_client
from tests.file_upload_support import (
    LEARNER_FOLDER_ID,
    sessions_without_a_home_folder,
    storage_directory,
    upload,
)
from tests.support import USER_ID, authorization

_WIDE_EXTENSION = "\U0001f600" * 110
_GUARD_LENGTH = 255


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    return sessions_without_a_home_folder()


@pytest.fixture
def strict(sessions: sessionmaker[Session]) -> Iterator[TestClient]:
    yield from scoped_client(sessions)


def test_removing_a_wide_absent_name_raises_nothing(
    tmp_path: Path,
) -> None:
    absent = {
        "file_id": str(uuid4()),
        "extension": _WIDE_EXTENSION,
        "name": "notes",
    }

    assert len(uploader_module._storage_name(absent)) <= _GUARD_LENGTH

    with storage_directory(tmp_path):
        uploader_module._remove_uploaded_files_from_storage([absent])


def test_a_wide_upload_failure_reaches_the_caller_unchanged(
    strict: TestClient, tmp_path: Path
) -> None:
    with storage_directory(tmp_path), pytest.raises(
        OSError, match="too long"
    ) as raised:
        _ = upload(
            strict,
            LEARNER_FOLDER_ID,
            authorization(USER_ID),
            ("notes." + _WIDE_EXTENSION,),
        )

    assert raised.value.__context__ is None
