import uuid
from datetime import datetime

from hypothesis import given, settings
from hypothesis import strategies as st

from features.study_units.formatting import (
    _is_object_list,
    date_to_str,
    flashcard_results,
    prepare_content,
)
from shared.models import Flashcard

_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
_MOMENTS = st.datetimes(
    min_value=datetime(1000, 1, 1), max_value=datetime(9999, 12, 31)
)
_ITEM_TYPES = st.sampled_from(
    ["true_or_false", "short_answer", "multiple_choice", ""]
)
_CONTENTS = st.fixed_dictionaries(
    {},
    optional={
        "question": st.text(max_size=8),
        "statement": st.text(max_size=8),
        "is_true": st.booleans(),
        "true_option": st.text(max_size=8),
        "false_options": st.lists(st.text(max_size=8), max_size=3),
    },
)


def _flashcard(created_at: datetime, next_review: datetime | None) -> Flashcard:
    return Flashcard(
        id=1,
        deck_id=uuid.uuid4(),
        type="basic",
        next_review=next_review,
        content={"front": "a"},
        created_at=created_at,
        fsrs_card=None,
    )


@settings(max_examples=50)
@given(_MOMENTS)
def test_date_to_str_property_round_trips_to_the_second(
    moment: datetime,
) -> None:
    formatted = date_to_str(moment)

    assert datetime.strptime(formatted, _DATE_FORMAT) == moment.replace(
        microsecond=0
    )


@settings(max_examples=50)
@given(
    st.one_of(
        st.lists(st.integers(), max_size=3),
        st.tuples(st.integers()),
        st.dictionaries(st.text(max_size=3), st.integers(), max_size=2),
        st.text(max_size=5),
        st.none(),
    )
)
def test__is_object_list_property_admits_exactly_the_lists(
    value: object,
) -> None:
    assert _is_object_list(value) is isinstance(value, list)


@settings(max_examples=50)
@given(st.lists(st.tuples(_MOMENTS, st.one_of(st.none(), _MOMENTS)), max_size=5))
def test_flashcard_results_property_keeps_every_card_in_order(
    moments: list[tuple[datetime, datetime | None]],
) -> None:
    cards = [
        _flashcard(created_at, next_review)
        for created_at, next_review in moments
    ]
    results = flashcard_results(cards)

    assert len(results) == len(cards)
    assert [result["created_at"] for result in results] == [
        date_to_str(created_at) for created_at, _ in moments
    ]
    assert [result["next_review"] is None for result in results] == [
        next_review is None for _, next_review in moments
    ]


@settings(max_examples=50)
@given(_CONTENTS, _ITEM_TYPES)
def test_prepare_content_property_always_answers_with_the_same_shape(
    content: dict[str, object], item_type: str
) -> None:
    prepared = prepare_content(content, item_type)

    assert sorted(prepared) == ["question", "shuffled_options"]
    assert isinstance(prepared["shuffled_options"], list)
