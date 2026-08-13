import uuid
from collections.abc import Iterator

import pytest
from sqlalchemy.orm import Session, sessionmaker

from features.study_units_generation.prompts.tests_prompt import (
    get_test_system_prompt,
)
from features.study_units_generation.study_unit_source import (
    StudyUnitSource,
)
from features.study_units_generation.study_unit_writer import save_test
from shared.models import Folder, Test
from tests.support import USER_ID, in_memory_sessions

_SOURCE = StudyUnitSource(kind="file", reference="greece.pdf")


@pytest.fixture
def sessions() -> Iterator[sessionmaker[Session]]:
    factory = in_memory_sessions()

    with factory() as session:
        session.add(
            Folder(id=uuid.UUID(USER_ID), name="Home", user_id=USER_ID)
        )
        session.commit()

    yield factory


def test_only_the_asked_types_shape_the_output() -> None:
    prompt = get_test_system_prompt(("short_answer",))

    assert "short_answer_test_items" in prompt
    assert "multiple_choice_test_items" not in prompt
    assert "true_or_false_test_items" not in prompt


def test_several_asked_types_all_shape_the_output() -> None:
    prompt = get_test_system_prompt(("true_or_false", "short_answer"))

    assert "true_or_false_test_items" in prompt
    assert "short_answer_test_items" in prompt


def test_no_asked_type_falls_back_to_multiple_choice() -> None:
    prompt = get_test_system_prompt(())

    assert "multiple_choice_test_items" in prompt


def test_an_unknown_asked_type_falls_back_to_multiple_choice() -> None:
    prompt = get_test_system_prompt(("essay",))

    assert "multiple_choice_test_items" in prompt
    assert "essay" not in prompt


def test_each_group_keeps_its_own_item_type(
    sessions: sessionmaker[Session],
) -> None:
    generated = {
        "multiple_choice_test_items": [{"question": "q"}],
        "true_or_false_test_items": [{"statement": "s", "is_true": True}],
        "short_answer_test_items": [{"question": "q", "answer": "a"}],
    }

    with sessions() as session:
        test_id = save_test(session, USER_ID, "Greece", generated, _SOURCE)

    with sessions() as session:
        saved = session.query(Test).filter_by(id=test_id).one()
        stored = {item.type for item in saved.test_items}

    assert stored == {"multiple_choice", "true_or_false", "short_answer"}


def test_only_dictionary_items_are_saved(
    sessions: sessionmaker[Session],
) -> None:
    generated = {"short_answer_test_items": [{"question": "q"}, "junk"]}

    with sessions() as session:
        test_id = save_test(session, USER_ID, "Greece", generated, _SOURCE)

    with sessions() as session:
        saved = session.query(Test).filter_by(id=test_id).one()
        stored = len(saved.test_items)

    assert stored == 1



def test_the_output_format_is_one_json_object() -> None:
    prompt = get_test_system_prompt(("short_answer", "true_or_false"))
    block = prompt.split("JSON```")[1].split("```")[0].strip()

    assert block.startswith("{")
    assert block.endswith("}")
