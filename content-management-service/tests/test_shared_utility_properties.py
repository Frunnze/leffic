import json
import uuid
from datetime import UTC, datetime
from unittest import mock

import pytest
from fastapi import HTTPException
from hypothesis import given, settings
from hypothesis import strategies as st

from features.study_units import clock
from shared.folder_tree import subfolder_ids
from shared.identifiers import parsed_identifier
from shared.json_extraction import _is_object_dict, get_dict_from_text

_NOT_FOUND = 404

_PLAIN_TEXT = st.text(
    alphabet=st.characters(
        min_codepoint=32, max_codepoint=126, blacklist_characters="\\\"'{}"
    ),
    min_size=1,
    max_size=12,
)
_FLAT_OBJECTS = st.dictionaries(
    _PLAIN_TEXT, st.integers(), min_size=1, max_size=5
)
_MISSING_DETAIL = "Deck not found"


class _FrozenClock:
    def __init__(self, moment: datetime) -> None:
        self.moment: datetime = moment

    def now(self, tz: object = None) -> datetime:
        _ = tz

        return self.moment


@settings(max_examples=50)
@given(_FLAT_OBJECTS)
def test_get_dict_from_text_property_round_trips_a_json_object(
    payload: dict[str, int],
) -> None:
    surrounded = f"Here you go: {json.dumps(payload)} hope that helps"

    assert get_dict_from_text(surrounded) == payload


@settings(max_examples=50)
@given(
    st.one_of(
        st.dictionaries(_PLAIN_TEXT, st.integers(), max_size=3),
        st.lists(st.integers(), max_size=3),
        st.integers(),
        st.text(max_size=5),
        st.none(),
    )
)
def test__is_object_dict_property_admits_exactly_the_mappings(
    value: object,
) -> None:
    assert _is_object_dict(value) is isinstance(value, dict)


@settings(max_examples=50)
@given(st.uuids())
def test_parsed_identifier_property_round_trips_a_uuid(
    identifier: uuid.UUID,
) -> None:
    assert parsed_identifier(str(identifier), _MISSING_DETAIL) == identifier


@settings(max_examples=50)
@given(st.text(max_size=40).filter(lambda text: not _is_a_uuid(text)))
def test_parsed_identifier_property_reports_unparsable_text_as_missing(
    identifier_text: str,
) -> None:
    with pytest.raises(HTTPException) as raised:
        _ = parsed_identifier(identifier_text, _MISSING_DETAIL)

    assert raised.value.status_code == _NOT_FOUND
    assert raised.value.detail == _MISSING_DETAIL


@settings(max_examples=50)
@given(st.datetimes(timezones=st.just(UTC)))
def test_utc_today_property_reads_the_date_in_utc(moment: datetime) -> None:
    with mock.patch.object(clock, "datetime", _FrozenClock(moment)):
        assert clock.utc_today() == moment.date()


@settings(max_examples=50)
@given(st.uuids(), st.one_of(st.none(), st.uuids()))
def test_subfolder_ids_property_filters_by_owner_only_when_asked(
    folder_id: uuid.UUID, user_id: uuid.UUID | None
) -> None:
    owner = None if user_id is None else str(user_id)
    statement = str(subfolder_ids(str(folder_id), owner))

    assert ("user_id" in statement) is (user_id is not None)


def _is_a_uuid(text: str) -> bool:
    try:
        _ = uuid.UUID(text)
    except ValueError:
        return False

    return True
