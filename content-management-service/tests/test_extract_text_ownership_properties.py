from hypothesis import given, settings
from hypothesis import strategies as st

from tests.access_support import MISSING_FILE, identifier_spellings
from tests.extraction_support import (
    NOT_FOUND,
    extract,
    file_entries,
    recorded_file_id,
)
from tests.hostile_identifiers import HOSTILE_IDENTIFIERS
from tests.property_support import property_world
from tests.support import OTHER_USER_ID, USER_ID, authorization

_CLIENT, _SESSIONS = property_world()
_FOREIGN_FILE_ID = recorded_file_id(_SESSIONS, OTHER_USER_ID)
_UNOWNED_IDENTIFIERS = st.sampled_from(
    HOSTILE_IDENTIFIERS + identifier_spellings(_FOREIGN_FILE_ID)
)


@settings(max_examples=50, deadline=None)
@given(_UNOWNED_IDENTIFIERS)
def test__resolved_documents_property_refuses_every_unowned_identifier(
    identifier: str,
) -> None:
    code, body = extract(
        _CLIENT, file_entries(identifier), authorization(USER_ID)
    )

    assert code == NOT_FOUND
    assert body == {"detail": MISSING_FILE}
