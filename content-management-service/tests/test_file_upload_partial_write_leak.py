import shutil
from collections.abc import Iterator
from pathlib import Path
from typing import IO
from unittest import mock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from tests.access_support import crashless_client
from tests.file_upload_support import (
    LEARNER_FOLDER_ID,
    STORAGE_FAILURE_MESSAGE,
    names_in,
    numbered_filenames,
    sessions_without_a_home_folder,
    storage_directory,
    upload,
)
from tests.support import USER_ID, authorization

_COPY_FILE_OBJECT = "features.file_upload.file_uploader.shutil.copyfileobj"


class CopyThatDiesOnOneFile:
    def __init__(self, dying_index: int) -> None:
        self.dying_index: int = dying_index
        self.calls: int = 0

    def __call__(
        self, source: IO[bytes], destination: IO[bytes]
    ) -> None:
        current_call = self.calls
        self.calls += 1

        if current_call == self.dying_index:
            raise RuntimeError(STORAGE_FAILURE_MESSAGE)

        shutil.copyfileobj(source, destination)


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    return sessions_without_a_home_folder()


@pytest.fixture
def crashless(sessions: sessionmaker[Session]) -> Iterator[TestClient]:
    yield from crashless_client(sessions)


def test_a_write_that_dies_mid_copy_leaves_no_bytes_behind(
    crashless: TestClient, tmp_path: Path
) -> None:
    with storage_directory(tmp_path), mock.patch(
        _COPY_FILE_OBJECT, CopyThatDiesOnOneFile(dying_index=0)
    ):
        _ = upload(
            crashless,
            LEARNER_FOLDER_ID,
            authorization(USER_ID),
            numbered_filenames(1, "pdf"),
        )

    assert names_in(tmp_path) == set()


def test_no_file_survives_a_copy_that_dies_on_the_last_of_many(
    crashless: TestClient, tmp_path: Path
) -> None:
    with storage_directory(tmp_path), mock.patch(
        _COPY_FILE_OBJECT, CopyThatDiesOnOneFile(dying_index=2)
    ):
        _ = upload(
            crashless,
            LEARNER_FOLDER_ID,
            authorization(USER_ID),
            numbered_filenames(3, "pdf"),
        )

    assert names_in(tmp_path) == set()
