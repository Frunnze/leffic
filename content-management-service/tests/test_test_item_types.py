import uuid

import pytest
from sqlalchemy.orm import Session, sessionmaker

from features.study_units_generation.assessment_writer import (
    append_test_items,
    create_test,
)
from features.study_units_generation.prompts.prompt_file import (
    assessment_item_values,
    rendered_prompt,
)
from features.study_units_generation.study_unit_source import (
    StudyUnitSource,
)
from features.study_units_generation.study_unit_types import (
    study_unit_type,
)
from shared.models import Folder, Test
from tests.support import USER_ID, in_memory_sessions

_SOURCE = StudyUnitSource(kind="file", reference="greece.pdf")
_ITEM_TYPES = ("multiple_choice", "true_or_false", "short_answer")


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    factory = in_memory_sessions()

    with factory() as session:
        session.add(
            Folder(id=uuid.UUID(USER_ID), name="Home", user_id=USER_ID)
        )
        session.commit()

    return factory


def _prompt_for(item_type: str) -> str:
    return rendered_prompt(
        study_unit_type(item_type).prompt_file, assessment_item_values(10)
    )


@pytest.mark.parametrize("item_type", _ITEM_TYPES)
def test_only_the_asked_type_shapes_the_output(item_type: str) -> None:
    prompt = _prompt_for(item_type)
    others = [other for other in _ITEM_TYPES if other != item_type]

    assert f"{item_type}_test_items" in prompt
    assert all(f"{other}_test_items" not in prompt for other in others)


@pytest.mark.parametrize("item_type", _ITEM_TYPES)
def test_every_type_asks_for_a_test_name(item_type: str) -> None:
    assert '"test_name"' in _prompt_for(item_type)


@pytest.mark.parametrize("item_type", _ITEM_TYPES)
def test_the_output_format_is_one_json_object(item_type: str) -> None:
    prompt = _prompt_for(item_type)
    block = prompt.split("JSON```")[1].split("```")[0].strip()

    assert block.startswith("{")
    assert block.endswith("}")


def test_each_group_keeps_its_own_item_type(
    sessions: sessionmaker[Session],
) -> None:
    generated = {
        "multiple_choice": [{"question": "q"}],
        "true_or_false": [{"statement": "s", "is_true": True}],
        "short_answer": [{"question": "q", "answer": "a"}],
    }

    with sessions() as session:
        test_id = create_test(session, USER_ID, _SOURCE)

        for item_type, items in generated.items():
            _ = append_test_items(session, test_id, item_type, items)

    with sessions() as session:
        saved = session.query(Test).filter_by(id=test_id).one()
        stored = {item.type for item in saved.test_items}

    assert stored == set(_ITEM_TYPES)


def test_only_dictionary_items_are_saved(
    sessions: sessionmaker[Session],
) -> None:
    with sessions() as session:
        test_id = create_test(session, USER_ID, _SOURCE)
        written = append_test_items(
            session, test_id, "short_answer", [{"question": "q"}, "junk"]
        )

    with sessions() as session:
        saved = session.query(Test).filter_by(id=test_id).one()
        stored = len(saved.test_items)

    assert written == 1
    assert stored == 1
