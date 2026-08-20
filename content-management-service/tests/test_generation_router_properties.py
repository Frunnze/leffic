import uuid
from unittest import mock

from hypothesis import given, settings
from hypothesis import strategies as st

from features.study_units_generation import generation_router
from features.study_units_generation.generation_router import (
    FlashcardsMetadata,
    GenerationRequest,
    TestMetadata,
    _queued_flashcards,
    _queued_test,
)
from features.study_units_generation.study_unit_source import (
    StudyUnitSource,
)
from shared.models import FlashcardDeck, Test
from tests.folder_seeding import seeded_folder
from tests.property_fakes import RecordingQueuedTask
from tests.support import in_memory_sessions

_SESSIONS = in_memory_sessions()
_NO_SOURCE = StudyUnitSource(kind=None, reference=None)
_FLASHCARD_TYPES = st.lists(
    st.sampled_from(["basic", "cloze", "feynman", "list"]),
    min_size=1,
    max_size=4,
    unique=True,
)
_ITEM_TYPES = st.lists(
    st.sampled_from(["multiple_choice", "true_or_false", "short_answer"]),
    min_size=1,
    max_size=3,
    unique=True,
)


def _cards_request(types: list[str]) -> GenerationRequest:
    wanted = FlashcardsMetadata.model_validate(
        {
            "types": types,
            "amount": 7,
            "comprehensiveness": "high",
            "verbosity": "high",
        }
    )

    return GenerationRequest(
        text="material", flashcards=wanted, ai_model="gpt-4.1-nano"
    )


def _test_request(types: list[str]) -> GenerationRequest:
    wanted = TestMetadata.model_validate({"types": types, "amount": 7})

    return GenerationRequest(
        text="material", test=wanted, ai_model="gpt-4.1-nano"
    )


@settings(max_examples=25, deadline=None)
@given(st.uuids(), _FLASHCARD_TYPES)
def test__queued_flashcards_property_queues_one_job_for_every_type(
    owner: uuid.UUID, types: list[str]
) -> None:
    request_data = _cards_request(types)
    queued_task = RecordingQueuedTask("queued")

    with _SESSIONS() as session:
        folder_id = seeded_folder(session, owner, {})

        with mock.patch.object(
            generation_router,
            "generate_flashcards_of_type_task",
            queued_task,
        ):
            queued = _queued_flashcards(
                request_data, str(folder_id), session, _NO_SOURCE
            )

        deck = session.get(
            FlashcardDeck, uuid.UUID(str(queued["flashcard_deck_id"]))
        )

    assert deck is not None
    assert queued["flashcard_task_ids"] == ["queued"] * len(types)
    assert [call["flashcard_type"] for call in queued_task.calls] == types
    assert all(
        call
        == {
            "ai_model": "gpt-4.1-nano",
            "extracted_text": "material",
            "deck_id": queued["flashcard_deck_id"],
            "flashcard_type": call["flashcard_type"],
            "settings": {
                "comprehensiveness": "high",
                "verbosity": "high",
                "amount": 7,
            },
        }
        for call in queued_task.calls
    )


@settings(max_examples=25, deadline=None)
@given(st.uuids(), _ITEM_TYPES)
def test__queued_test_property_queues_one_job_for_every_type(
    owner: uuid.UUID, types: list[str]
) -> None:
    request_data = _test_request(types)
    queued_task = RecordingQueuedTask("queued")

    with _SESSIONS() as session:
        folder_id = seeded_folder(session, owner, {})

        with mock.patch.object(
            generation_router,
            "generate_test_items_of_type_task",
            queued_task,
        ):
            queued = _queued_test(
                request_data, str(folder_id), session, _NO_SOURCE
            )

        created = session.get(Test, uuid.UUID(str(queued["test_id"])))

    assert created is not None
    assert queued["test_task_ids"] == ["queued"] * len(types)
    assert [call["item_type"] for call in queued_task.calls] == types
    assert all(
        call
        == {
            "ai_model": "gpt-4.1-nano",
            "extracted_text": "material",
            "test_id": queued["test_id"],
            "item_type": call["item_type"],
            "amount": 7,
        }
        for call in queued_task.calls
    )


@settings(max_examples=25, deadline=None)
@given(st.uuids())
def test__queued_flashcards_property_falls_back_to_one_default_job(
    owner: uuid.UUID,
) -> None:
    request_data = _cards_request([])
    queued_task = RecordingQueuedTask("queued")

    with _SESSIONS() as session:
        folder_id = seeded_folder(session, owner, {})

        with mock.patch.object(
            generation_router,
            "generate_flashcards_of_type_task",
            queued_task,
        ):
            queued = _queued_flashcards(
                request_data, str(folder_id), session, _NO_SOURCE
            )

    assert queued["flashcard_task_ids"] == ["queued"]


@settings(max_examples=25, deadline=None)
@given(st.uuids())
def test__queued_test_property_falls_back_to_one_default_job(
    owner: uuid.UUID,
) -> None:
    request_data = _test_request([])
    queued_task = RecordingQueuedTask("queued")

    with _SESSIONS() as session:
        folder_id = seeded_folder(session, owner, {})

        with mock.patch.object(
            generation_router,
            "generate_test_items_of_type_task",
            queued_task,
        ):
            queued = _queued_test(
                request_data, str(folder_id), session, _NO_SOURCE
            )

    assert queued["test_task_ids"] == ["queued"]
