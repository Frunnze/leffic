"""
Bug hunt: owned_content joins File to Folder and filters on
Folder.user_id, so a File row with a NULL/dangling folder_id could,
in principle, produce a false negative (never joinable, so it is
always unreachable, effectively orphaned and undeletable) or a false
positive (joined to nobody's folder) ownership result. Oracle: exact
expected value -- the schema itself must make a folderless File
impossible to persist, closing that gap.

Concrete inputs -> expected outputs:
- input: File(id=<uuid>, name="orphan", extension="pdf") committed
  without a folder_id
  output: sqlalchemy.exc.IntegrityError is raised on commit (the
  files.folder_id column is NOT NULL), so no File row can ever exist
  without a real, joinable Folder.
"""

import uuid

import pytest
from sqlalchemy.exc import IntegrityError

from shared.models import File
from tests.support import in_memory_sessions


def test_a_file_without_a_folder_cannot_be_stored() -> None:
    factory = in_memory_sessions()

    with factory() as session:
        session.add(File(id=uuid.uuid4(), name="orphan", extension="pdf"))

        with pytest.raises(IntegrityError):
            session.commit()
