import importlib
import inspect

import pytest
from fastapi import HTTPException

from features.file_system import bookmark_router, content_router
from shared import file_access
from shared.file_access import owned_file
from tests.access_support import MISSING_FILE
from tests.extraction_support import recorded_file_id
from tests.property_support import property_world
from tests.support import OTHER_USER_ID, USER_ID

_RETIRED_MODULE = "features.file_system.file_access"
_SHARED_IMPORT = "from shared.file_access import owned_file"
_NOT_FOUND = 404
_, _SESSIONS = property_world()


def test_owned_file_is_importable_from_shared() -> None:
    assert callable(owned_file)

    with pytest.raises(ModuleNotFoundError):
        _ = importlib.import_module(_RETIRED_MODULE)


def test_missing_file_detail_is_unchanged() -> None:
    assert file_access._MISSING_FILE == MISSING_FILE


def test_content_router_imports_the_shared_helper() -> None:
    source = inspect.getsource(content_router)

    assert _SHARED_IMPORT in source
    assert _RETIRED_MODULE not in source


def test_bookmark_router_imports_the_shared_helper() -> None:
    source = inspect.getsource(bookmark_router)

    assert _SHARED_IMPORT in source
    assert _RETIRED_MODULE not in source


def test_owned_file_hands_back_the_callers_own_row() -> None:
    file_id = recorded_file_id(_SESSIONS, USER_ID)

    with _SESSIONS() as session:
        found = owned_file(session, USER_ID, file_id)

    assert str(found.id) == file_id


def test_owned_file_refuses_a_row_owned_by_someone_else() -> None:
    file_id = recorded_file_id(_SESSIONS, OTHER_USER_ID)

    with _SESSIONS() as session, pytest.raises(HTTPException) as refusal:
        _ = owned_file(session, USER_ID, file_id)

    assert refusal.value.status_code == _NOT_FOUND
    assert refusal.value.detail == MISSING_FILE
