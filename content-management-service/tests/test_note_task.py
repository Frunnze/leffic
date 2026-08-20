import uuid
from unittest import mock

import pytest
from sqlalchemy.orm import Session, sessionmaker

from features.study_units_generation import generation_tasks
from shared.models import Folder, Note
from tests.support import USER_ID, in_memory_sessions

HOME_ID = uuid.UUID(USER_ID)
_TEXT = "some study material"


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


def _run_note(
    answer: object,
    sessions: sessionmaker[Session],
    factory: FakeFactory | None = None,
    model: str | None = None,
) -> dict[str, object]:
    with (
        mock.patch.object(
            generation_tasks,
            "ai_factory",
            factory or FakeFactory(FakeAi(answer)),
        ),
        mock.patch.object(generation_tasks, "SessionLocal", sessions),
    ):
        return generation_tasks._generate_note_task(
            ai_model=model,
            extracted_text=_TEXT,
            folder_id=USER_ID,
            source_kind="topic",
            source_reference="roman empire",
        )


def test_a_generated_note_lands_with_its_content(
    sessions: sessionmaker[Session],
) -> None:
    result = _run_note(
        {"note_name": "Neurons", "note_content": "<p>Hi</p>"}, sessions
    )

    with sessions() as session:
        note = session.query(Note).one()

        assert result == {"note_id": str(note.id), "note_name": "Neurons"}
        assert note.name == "Neurons"
        assert note.source_kind == "topic"
        assert note.source_reference == "roman empire"
        assert note.content == "<p>Hi</p>"
        assert note.type == "general"


def test_the_note_task_asks_for_a_note(
    sessions: sessionmaker[Session],
) -> None:
    factory = FakeFactory(
        FakeAi({"note_name": "Neurons", "note_content": "<p>Hi</p>"})
    )

    _ = _run_note({}, sessions, factory)

    assert "note_content" in factory.ai.prompts[0]
    assert factory.ai.prompts[1] == _TEXT


def test_the_note_task_uses_the_chosen_model(
    sessions: sessionmaker[Session],
) -> None:
    factory = FakeFactory(
        FakeAi({"note_name": "Neurons", "note_content": "<p>Hi</p>"})
    )

    _ = _run_note({}, sessions, factory, "gpt-4.1-nano")

    assert factory.models == ["gpt-4.1-nano"]
