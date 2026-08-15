import uuid

import pytest
from fastapi import HTTPException
from hypothesis import given, settings
from hypothesis import strategies as st

from features.file_system.unit_router import (
    _content_model,
    _move_folder,
    _owned_unit,
    _validated_name,
)
from shared.models import File, FlashcardDeck, Note, Test
from tests.folder_seeding import seeded_folder
from tests.property_support import property_world, seeded_file
from tests.support import authorization

_OK = 200
_UNPROCESSABLE = 422
_NOT_FOUND = 404
_CLIENT, _SESSIONS = property_world()
_KNOWN_TYPES = {
    "flashcard_deck": FlashcardDeck,
    "test": Test,
    "note": Note,
    "file": File,
}
_UNKNOWN_TYPES = st.sampled_from(["folder", "", "deck", "FILE", "notes"])
_BLANK = st.sampled_from(["", " ", "\t", "  \n "])


@settings(max_examples=50)
@given(st.sampled_from(sorted(_KNOWN_TYPES)))
def test__content_model_property_maps_each_known_type_to_its_model(
    unit_type: str,
) -> None:
    assert _content_model(unit_type) is _KNOWN_TYPES[unit_type]


@settings(max_examples=25)
@given(_UNKNOWN_TYPES)
def test__content_model_property_refuses_a_type_it_does_not_know(
    unit_type: str,
) -> None:
    with pytest.raises(HTTPException) as raised:
        _ = _content_model(unit_type)

    assert raised.value.status_code == _UNPROCESSABLE


@settings(max_examples=50)
@given(st.text(min_size=1, max_size=12), _BLANK, _BLANK)
def test__validated_name_property_trims_the_space_around_a_name(
    name: str, before: str, after: str
) -> None:
    padded = f"{before}{name}{after}"

    if not padded.strip():
        with pytest.raises(HTTPException):
            _ = _validated_name(padded)

        return

    assert _validated_name(padded) == padded.strip()


@settings(max_examples=25, deadline=None)
@given(st.uuids(), st.uuids())
def test__owned_unit_property_never_reaches_a_strangers_unit(
    owner: uuid.UUID, stranger: uuid.UUID
) -> None:
    with _SESSIONS() as session:
        file_id = seeded_file(session, owner)

        assert (
            _owned_unit(session, str(owner), str(file_id), "file").id
            == file_id
        )

        with pytest.raises(HTTPException) as raised:
            _ = _owned_unit(session, str(stranger), str(file_id), "file")

    assert raised.value.status_code == _NOT_FOUND


@settings(max_examples=25, deadline=None)
@given(st.uuids(), st.text(min_size=1, max_size=10))
def test_rename_unit_property_stores_the_trimmed_name(
    owner: uuid.UUID, name: str
) -> None:
    with _SESSIONS() as session:
        file_id = seeded_file(session, owner)

    response = _CLIENT.patch(
        "/rename-unit",
        json={
            "unit_id": str(file_id),
            "unit_type": "file",
            "name": f"  {name}  ",
        },
        headers=authorization(str(owner)),
    )

    with _SESSIONS() as session:
        renamed = session.get(File, file_id)

        assert renamed is not None
        assert renamed.name == name.strip() or not name.strip()

    assert response.status_code in (_OK, _UNPROCESSABLE)


@settings(max_examples=25, deadline=None)
@given(st.uuids())
def test_move_unit_property_puts_the_unit_in_the_named_folder(
    owner: uuid.UUID,
) -> None:
    with _SESSIONS() as session:
        file_id = seeded_file(session, owner)
        destination = seeded_folder(session, owner, {})

    response = _CLIENT.patch(
        "/move-unit",
        json={
            "unit_id": str(file_id),
            "unit_type": "file",
            "folder_id": str(destination),
        },
        headers=authorization(str(owner)),
    )

    with _SESSIONS() as session:
        moved = session.get(File, file_id)

        assert moved is not None
        assert moved.folder_id == destination

    assert response.status_code == _OK


@settings(max_examples=25, deadline=None)
@given(st.uuids())
def test__move_folder_property_refuses_to_put_a_folder_inside_itself(
    owner: uuid.UUID,
) -> None:
    with _SESSIONS() as session:
        folder_id = seeded_folder(session, owner, {})

        with pytest.raises(HTTPException) as raised:
            _move_folder(
                session, str(owner), str(folder_id), str(folder_id)
            )

    assert raised.value.status_code == _UNPROCESSABLE
