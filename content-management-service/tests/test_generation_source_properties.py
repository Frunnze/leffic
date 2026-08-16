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
    _queued_tasks,
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


@settings(max_examples=25, deadline=None)
@given(st.uuids())
def test__queued_flashcards_property_falls_back_to_the_default_settings(
    owner: uuid.UUID,
) -> None:
    wanted = FlashcardsMetadata.model_validate(
        {"types": ["basic"], "comprehensiveness": None, "verbosity": None}
    )
    request_data = GenerationRequest(text="material", flashcards=wanted)
    queued_task = RecordingQueuedTask("queued")

    with _SESSIONS() as session:
        folder_id = seeded_folder(session, owner, {})

        with mock.patch.object(
            generation_router,
            "generate_flashcards_of_type_task",
            queued_task,
        ):
            _ = _queued_flashcards(
                request_data, str(folder_id), session, _NO_SOURCE
            )

    assert queued_task.calls[0]["comprehensiveness"] == "medium"
    assert queued_task.calls[0]["verbosity"] == "low"


@settings(max_examples=25, deadline=None)
@given(st.uuids())
def test__queued_tasks_property_stamps_the_source_on_what_it_creates(
    owner: uuid.UUID,
) -> None:
    request_data = GenerationRequest(
        text="material",
        source_kind="link",
        source_reference="https://example.com/x",
        flashcards=FlashcardsMetadata.model_validate({"types": ["basic"]}),
        test=TestMetadata.model_validate({"types": ["short_answer"]}),
    )
    queued_task = RecordingQueuedTask("queued")

    with _SESSIONS() as session:
        folder_id = seeded_folder(session, owner, {})

        with mock.patch.object(
            generation_router,
            "generate_flashcards_of_type_task",
            queued_task,
        ), mock.patch.object(
            generation_router,
            "generate_test_items_of_type_task",
            queued_task,
        ):
            queued = _queued_tasks(
                request_data, str(folder_id), session
            )

        deck = session.get(
            FlashcardDeck, uuid.UUID(str(queued["flashcard_deck_id"]))
        )
        created = session.get(Test, uuid.UUID(str(queued["test_id"])))

    assert deck is not None
    assert deck.source_kind == "link"
    assert deck.source_reference == "https://example.com/x"
    assert created is not None
    assert created.source_kind == "link"
    assert created.source_reference == "https://example.com/x"
