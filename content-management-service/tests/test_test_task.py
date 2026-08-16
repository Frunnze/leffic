import uuid
from unittest import mock

import pytest
from sqlalchemy.orm import Session, sessionmaker

from features.study_units_generation import generation_tasks
from features.study_units_generation.assessment_writer import (
    create_test,
)
from features.study_units_generation.study_unit_source import (
    StudyUnitSource,
)
from shared.models import Folder, Test, TestItem
from tests.support import USER_ID, in_memory_sessions

HOME_ID = uuid.UUID(USER_ID)
_TEXT = "some study material"
_SOURCE = StudyUnitSource(kind="file", reference="biology.pdf")


class FakeAi:
    def __init__(self, answer: object) -> None:
        super().__init__()
        self.answer: object = answer
        self.prompts: list[str] = []

    def get_ai_res(
        self, system_prompt: str, user_prompt: str
    ) -> tuple[object, float | None]:
        self.prompts.append(system_prompt)
        self.prompts.append(user_prompt)

        return self.answer, None


class FakeFactory:
    def __init__(self, ai: FakeAi) -> None:
        super().__init__()
        self.ai: FakeAi = ai
        self.models: list[str | None] = []

    def get_ai(self, model: str | None = None) -> FakeAi:
        self.models.append(model)

        return self.ai


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    factory = in_memory_sessions()

    with factory() as session:
        session.add(Folder(id=HOME_ID, name="Home", user_id=HOME_ID))
        session.commit()

    return factory


def _run_test(
    answer: object,
    sessions: sessionmaker[Session],
    factory: FakeFactory | None = None,
    model: str | None = None,
) -> dict[str, object]:
    with sessions() as session:
        test_id = create_test(session, USER_ID, _SOURCE)

    with (
        mock.patch.object(
            generation_tasks,
            "ai_factory",
            factory or FakeFactory(FakeAi(answer)),
        ),
        mock.patch.object(generation_tasks, "SessionLocal", sessions),
    ):
        return generation_tasks._generate_test_items_of_type_task(
            ai_model=model,
            extracted_text=_TEXT,
            test_id=test_id,
            item_type="multiple_choice",
            amount=10,
        )


def test_a_generated_test_lands_with_its_items(
    sessions: sessionmaker[Session],
) -> None:
    result = _run_test(
        {
            "test_name": "Neurons",
            "multiple_choice_test_items": [{"question": "q"}],
        },
        sessions,
    )

    with sessions() as session:
        test = session.query(Test).one()
        item = session.query(TestItem).one()

        assert result == {
            "test_id": str(test.id),
            "type": "multiple_choice",
            "written": 1,
        }
        assert test.name == "Neurons"
        assert test.source_kind == "file"
        assert test.source_reference == "biology.pdf"
        assert item.content == {"question": "q"}
        assert item.type == "multiple_choice"


def test_a_test_without_a_list_of_items_saves_none(
    sessions: sessionmaker[Session],
) -> None:
    _ = _run_test(
        {"test_name": "Neurons", "multiple_choice_test_items": "oops"},
        sessions,
    )

    with sessions() as session:
        assert session.query(TestItem).all() == []


def test_only_dictionaries_survive_as_test_items(
    sessions: sessionmaker[Session],
) -> None:
    _ = _run_test(
        {
            "test_name": "Neurons",
            "multiple_choice_test_items": [{"question": "q"}, "junk"],
        },
        sessions,
    )

    with sessions() as session:
        items = session.query(TestItem).all()

        assert len(items) == 1
        assert items[0].content == {"question": "q"}




def test_the_test_task_uses_the_chosen_model(
    sessions: sessionmaker[Session],
) -> None:
    factory = FakeFactory(
        FakeAi({"test_name": "Neurons", "multiple_choice_test_items": []})
    )

    _ = _run_test({}, sessions, factory, "gpt-4.1-nano")

    assert factory.models == ["gpt-4.1-nano"]


def test_a_test_item_field_that_cannot_be_iterated_saves_none(
    sessions: sessionmaker[Session],
) -> None:
    _ = _run_test(
        {"test_name": "Neurons", "multiple_choice_test_items": 42}, sessions
    )

    with sessions() as session:
        assert session.query(TestItem).all() == []


def test_the_test_task_asks_for_test_items(
    sessions: sessionmaker[Session],
) -> None:
    factory = FakeFactory(
        FakeAi(
            {
                "test_name": "Neurons",
                "multiple_choice_test_items": [{"question": "q"}],
            }
        )
    )

    _ = _run_test({}, sessions, factory)

    assert "multiple_choice_test_items" in factory.ai.prompts[0]
    assert factory.ai.prompts[1] == _TEXT
