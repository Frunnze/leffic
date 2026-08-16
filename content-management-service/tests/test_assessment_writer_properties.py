import uuid

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from features.study_units_generation.assessment_writer import (
    MissingTestError,
    _existing_test,
    append_test_items,
    create_test,
    name_test_once,
)
from features.study_units_generation.study_unit_source import (
    StudyUnitSource,
)
from features.study_units_generation.study_unit_writer import PENDING_NAME
from shared.models import Test, TestItem
from tests.folder_seeding import seeded_folder
from tests.support import in_memory_sessions

_SESSIONS = in_memory_sessions()
_NO_SOURCE = StudyUnitSource(kind=None, reference=None)
_ITEM = st.fixed_dictionaries({"question": st.text(max_size=6)})
_TYPES = st.sampled_from(
    ["multiple_choice", "true_or_false", "short_answer"]
)
_NAMES = st.text(min_size=1, max_size=10).filter(
    lambda name: name != PENDING_NAME
)


@settings(max_examples=25, deadline=None)
@given(st.uuids(), st.uuids())
def test__existing_test_property_refuses_a_test_that_is_not_there(
    owner: uuid.UUID, absent: uuid.UUID
) -> None:
    with _SESSIONS() as session:
        folder_id = seeded_folder(session, owner, {})
        test_id = create_test(session, str(folder_id), _NO_SOURCE)

        assert str(_existing_test(session, test_id).id) == test_id

        with pytest.raises(MissingTestError) as refused:
            _ = _existing_test(session, str(absent))

        assert str(refused.value) == "Test does not exist!"


@settings(max_examples=25, deadline=None)
@given(st.uuids())
def test_create_test_property_starts_out_awaiting_its_name(
    owner: uuid.UUID,
) -> None:
    with _SESSIONS() as session:
        folder_id = seeded_folder(session, owner, {})
        test_id = create_test(session, str(folder_id), _NO_SOURCE)
        created = session.get(Test, uuid.UUID(test_id))

        assert created is not None
        assert created.name == PENDING_NAME
        assert str(created.folder_id) == str(folder_id)
        assert created.test_items == []


@settings(max_examples=25, deadline=None)
@given(st.uuids(), _TYPES, st.lists(_ITEM, max_size=4))
def test_append_test_items_property_writes_every_item_under_its_type(
    owner: uuid.UUID, item_type: str, items: list[dict[str, str]]
) -> None:
    with _SESSIONS() as session:
        folder_id = seeded_folder(session, owner, {})
        test_id = create_test(session, str(folder_id), _NO_SOURCE)
        written = append_test_items(session, test_id, item_type, items)
        saved = (
            session.query(TestItem)
            .filter(TestItem.test_id == uuid.UUID(test_id))
            .all()
        )

        assert written == len(items)
        assert len(saved) == len(items)
        assert all(item.type == item_type for item in saved)


@settings(max_examples=25, deadline=None)
@given(st.uuids(), _TYPES, st.lists(_ITEM, max_size=3))
def test_append_test_items_property_adds_to_what_is_already_there(
    owner: uuid.UUID, item_type: str, items: list[dict[str, str]]
) -> None:
    with _SESSIONS() as session:
        folder_id = seeded_folder(session, owner, {})
        test_id = create_test(session, str(folder_id), _NO_SOURCE)
        first = append_test_items(
            session, test_id, "multiple_choice", items
        )
        second = append_test_items(session, test_id, item_type, items)
        saved = (
            session.query(TestItem)
            .filter(TestItem.test_id == uuid.UUID(test_id))
            .all()
        )

        assert len(saved) == first + second


@settings(max_examples=25, deadline=None)
@given(st.uuids(), _NAMES, _NAMES)
def test_name_test_once_property_keeps_the_first_name_it_was_given(
    owner: uuid.UUID, winning_name: str, later_name: str
) -> None:
    with _SESSIONS() as session:
        folder_id = seeded_folder(session, owner, {})
        test_id = create_test(session, str(folder_id), _NO_SOURCE)

        untouched_id = create_test(session, str(folder_id), _NO_SOURCE)

        assert name_test_once(session, test_id, winning_name)
        assert not name_test_once(session, test_id, later_name)

        named = session.get(Test, uuid.UUID(test_id))
        untouched = session.get(Test, uuid.UUID(untouched_id))

        assert named is not None
        assert named.name == winning_name
        assert untouched is not None
        assert untouched.name == PENDING_NAME
