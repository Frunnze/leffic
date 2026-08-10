import uuid
from unittest import mock

import pytest
from sqlalchemy.orm import Session, sessionmaker

from features.study_units_generation import generation_tasks
from features.study_units_generation.generation_tasks import (
    FlashcardsMetadata,
)
from shared.models import Flashcard, FlashcardDeck, Folder
from tests.support import USER_ID, in_memory_sessions

HOME_ID = uuid.UUID(USER_ID)
_TEXT = "some study material"
_METADATA: FlashcardsMetadata = {
    "comprehensiveness": "high",
    "verbosity": "high",
    "types": ["cloze"],
    "amount": 5,
}


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


def _generate(
    answer: object, sessions: sessionmaker[Session], model: str | None = None
) -> tuple[dict[str, object], FakeFactory]:
    factory = FakeFactory(FakeAi(answer))

    with (
        mock.patch.object(generation_tasks, "ai_factory", factory),
        mock.patch.object(generation_tasks, "SessionLocal", sessions),
    ):
        result = generation_tasks._generate_flashcards_task(
            ai_model=model,
            extracted_text=_TEXT,
            flashcards_metadata=_METADATA,
            folder_id=USER_ID,
        )

    return result, factory


def test_generated_flashcards_land_in_a_new_deck(
    sessions: sessionmaker[Session],
) -> None:
    result, _unused = _generate(
        {
            "deck_name": "Neurons",
            "cloze_flashcards": [{"text": "a", "hidden_parts": ["a"]}],
        },
        sessions,
    )

    with sessions() as session:
        deck = session.query(FlashcardDeck).one()
        card = session.query(Flashcard).one()

        assert result == {
            "flashcard_deck_id": str(deck.id),
            "deck_name": "Neurons",
        }
        assert deck.name == "Neurons"
        assert card.type == "cloze"
        assert card.content == {"text": "a", "hidden_parts": ["a"]}


def test_the_deck_name_is_not_stored_as_a_flashcard(
    sessions: sessionmaker[Session],
) -> None:
    _unused, _factory = _generate(
        {
            "deck_name": "Neurons",
            "basic_flashcards": [{"front": "q", "back": "a"}],
        },
        sessions,
    )

    with sessions() as session:
        cards = session.query(Flashcard).all()

        assert len(cards) == 1
        assert cards[0].content == {"front": "q", "back": "a"}


def test_generation_asks_the_chosen_model_for_the_chosen_types(
    sessions: sessionmaker[Session],
) -> None:
    _unused, factory = _generate(
        {"deck_name": "Neurons", "cloze_flashcards": []},
        sessions,
        "gpt-4.1-nano",
    )

    prompt = factory.ai.prompts[0]

    assert factory.models == ["gpt-4.1-nano"]
    assert "cloze_flashcards" in prompt
    assert "Flashcards number: 5" in prompt
    assert "Comprehensiveness: high" in prompt
    assert "Flashcard verbosity: high" in prompt
    assert factory.ai.prompts[1] == _TEXT
