import uuid

from hypothesis import given, settings
from hypothesis import strategies as st

from tests.property_support import property_world, seeded_file
from tests.support import authorization

_OK = 200
_NOT_FOUND = 404
_PAGES = st.integers(min_value=1, max_value=500)
_CLIENT, _SESSIONS = property_world()


def _bookmarked(owner: uuid.UUID, page: int | None) -> uuid.UUID:
    with _SESSIONS() as session:
        return seeded_file(session, owner, page)


@settings(max_examples=25, deadline=None)
@given(st.uuids(), st.one_of(st.none(), _PAGES))
def test_get_file_bookmark_property_reports_the_page_that_was_stored(
    owner: uuid.UUID, page: int | None
) -> None:
    file_id = _bookmarked(owner, page)
    response = _CLIENT.get(
        "/file-bookmark",
        params={"file_id": str(file_id)},
        headers=authorization(str(owner)),
    )

    assert response.status_code == _OK
    assert response.json() == {"page": page}


@settings(max_examples=25, deadline=None)
@given(st.uuids(), _PAGES)
def test_set_file_bookmark_property_round_trips_the_chosen_page(
    owner: uuid.UUID, page: int
) -> None:
    file_id = _bookmarked(owner, None)
    written = _CLIENT.put(
        "/file-bookmark",
        json={"file_id": str(file_id), "page": page},
        headers=authorization(str(owner)),
    )
    read_back = _CLIENT.get(
        "/file-bookmark",
        params={"file_id": str(file_id)},
        headers=authorization(str(owner)),
    )

    assert written.json() == {"page": page}
    assert read_back.json() == {"page": page}


@settings(max_examples=25, deadline=None)
@given(st.uuids(), _PAGES)
def test_remove_file_bookmark_property_always_clears_the_page(
    owner: uuid.UUID, page: int
) -> None:
    file_id = _bookmarked(owner, page)
    removed = _CLIENT.delete(
        "/file-bookmark",
        params={"file_id": str(file_id)},
        headers=authorization(str(owner)),
    )

    assert removed.json() == {"page": None}


@settings(max_examples=25, deadline=None)
@given(st.uuids(), st.uuids(), _PAGES)
def test_get_file_bookmark_property_hides_another_owners_file(
    owner: uuid.UUID, stranger: uuid.UUID, page: int
) -> None:
    file_id = _bookmarked(owner, page)
    response = _CLIENT.get(
        "/file-bookmark",
        params={"file_id": str(file_id)},
        headers=authorization(str(stranger)),
    )

    assert response.status_code == _NOT_FOUND
