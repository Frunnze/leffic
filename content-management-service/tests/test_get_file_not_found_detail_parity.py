"""
Bug hunt: GET /file's 404 detail must not let a caller distinguish
"this file_id does not exist anywhere" from "this file_id exists but
belongs to someone else". Oracle: differential -- the detail for a
random unknown id and for another learner's real, owned id must be
byte-for-byte identical.

Concrete inputs -> expected outputs:
- input: GET /file?file_id=<uuid never inserted anywhere>&file_extension=pdf
  output: 404, {"detail": "File does not exist!"}
- input: GET /file?file_id=<a real file owned by a different learner>
  &file_extension=pdf
  output: 404, {"detail": "File does not exist!"} (identical detail,
  identical status -- so the two cases are indistinguishable to the
  caller).
"""

import uuid
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from tests.access_support import (
    HOME_ID,
    MISSING_FILE,
    OTHER_HOME_ID,
    OwnedContent,
    scoped_client,
    seeded_content,
)
from tests.support import authorization, in_memory_sessions

_NOT_FOUND = 404


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    return in_memory_sessions()


@pytest.fixture
def client(sessions: sessionmaker[Session]) -> Iterator[TestClient]:
    yield from scoped_client(sessions)


def test_an_unknown_id_and_a_strangers_id_read_the_same_404(
    client: TestClient, sessions: sessionmaker[Session]
) -> None:
    owned: OwnedContent = seeded_content(sessions, OTHER_HOME_ID)
    unknown_response = client.get(
        "/file",
        params={"file_id": str(uuid.uuid4()), "file_extension": "pdf"},
        headers=authorization(str(HOME_ID)),
    )
    strangers_response = client.get(
        "/file",
        params={"file_id": owned.file_id, "file_extension": "pdf"},
        headers=authorization(str(HOME_ID)),
    )

    assert unknown_response.status_code == _NOT_FOUND
    assert strangers_response.status_code == _NOT_FOUND
    assert unknown_response.json() == {"detail": MISSING_FILE}
    assert strangers_response.json() == unknown_response.json()
