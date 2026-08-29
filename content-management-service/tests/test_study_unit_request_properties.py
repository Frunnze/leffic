import uuid
from datetime import UTC, datetime
from typing import cast
from unittest import mock

from hypothesis import given, settings
from hypothesis import strategies as st

from features.study_units_generation import generation_router
from features.study_units_generation.extraction_router import (
    _extracted_text,
)
from features.study_units_generation.task_ownership import signed_task_id
from features.study_units_generation.text_sources import StoredDocument
from shared.models import Test, TestItem
from tests.folder_seeding import seeded_folder
from tests.property_fakes import (
    FakeAiFactory,
    FakeAiManager,
    FakeQueuedTask,
    UnavailableAiManager,
)
from tests.property_support import property_world
from tests.support import authorization

_OK = 200
_BAD_REQUEST = 400
_NOT_FOUND = 404
_UNAVAILABLE = 503
_CLIENT, _SESSIONS = property_world()
_TEXT = st.text(alphabet="abcdefg", min_size=1, max_size=12)
_EXTRACTION = "features.study_units_generation.extraction_router"
_TEXT_FROM_FILES = f"{_EXTRACTION}.text_from_files"
_TEXT_FROM_LINK = f"{_EXTRACTION}.text_from_link"
_CHATBOT_FACTORY = "features.chatbot.chatbot.ai_factory"


def _seeded_item(owner: uuid.UUID) -> int:
    with _SESSIONS() as session:
        folder_id = seeded_folder(session, owner, {})
        quiz = Test(
            id=uuid.uuid4(),
            name="Quiz",
            folder_id=folder_id,
            created_at=datetime.now(UTC),
            public=False,
        )
        quiz.test_items.append(
            TestItem(
                content={"question": "q"},
                type="multiple_choice",
                created_at=datetime.now(UTC),
            )
        )
        session.add(quiz)
        session.commit()

        return quiz.test_items[0].id


@settings(max_examples=50)
@given(_TEXT, st.sampled_from(["files", "link", "neither"]))
def test__extracted_text_property_reads_whichever_source_was_given(
    body: str, source: str
) -> None:
    documents = (
        [StoredDocument(storage_name="f.pdf", extension="pdf")]
        if source == "files"
        else []
    )
    link = "https://example.com" if source == "link" else None

    with (
        mock.patch(_TEXT_FROM_FILES, return_value=body),
        mock.patch(_TEXT_FROM_LINK, return_value=body),
    ):
        extracted = _extracted_text(documents, link)

    assert extracted == ("" if source == "neither" else body)


@settings(max_examples=25, deadline=None)
@given(st.uuids(), st.sampled_from(["", "   ", "\t\n"]))
def test_generate_study_units_property_refuses_text_that_is_only_space(
    owner: uuid.UUID, blank: str
) -> None:
    response = _CLIENT.post(
        "/generate-study-units",
        json={"text": blank, "folder_id": "home", "note": {}},
        headers=authorization(str(owner)),
    )

    assert response.status_code == _BAD_REQUEST


@settings(max_examples=25, deadline=None)
@given(st.uuids(), _TEXT)
def test__queued_tasks_property_queues_only_what_was_asked_for(
    owner: uuid.UUID, body: str
) -> None:
    queued = FakeQueuedTask("task-1")

    with mock.patch.object(
        generation_router, "generate_note_task", queued
    ), mock.patch.object(
        generation_router, "generate_flashcards_of_type_task", queued
    ):
        response = _CLIENT.post(
            "/generate-study-units",
            json={
                "text": body,
                "folder_id": "home",
                "note": {},
                "flashcards": None,
            },
            headers=authorization(str(owner)),
        )

    reported = cast("dict[str, object]", response.json())

    assert response.status_code == _OK
    assert reported == {
        "note_task_id": signed_task_id("task-1", str(owner))
    }


@settings(max_examples=25, deadline=None)
@given(st.uuids(), st.uuids())
def test_update_test_item_property_edits_only_the_owners_item(
    owner: uuid.UUID, stranger: uuid.UUID
) -> None:
    item_id = _seeded_item(owner)
    payload = {"test_item_id": item_id, "content": {"question": "new"}}
    refused = _CLIENT.patch(
        "/update-test-item",
        json=payload,
        headers=authorization(str(stranger)),
    )
    updated = _CLIENT.patch(
        "/update-test-item",
        json=payload,
        headers=authorization(str(owner)),
    )

    with _SESSIONS() as session:
        stored = session.get(TestItem, item_id)

        assert stored is not None
        assert stored.content == {"question": "new"}

    assert refused.status_code == _NOT_FOUND
    assert updated.status_code == _OK


@settings(max_examples=25, deadline=None)
@given(st.text(min_size=1, max_size=20))
def test_chat_property_answers_with_whatever_the_model_said(
    answer: str,
) -> None:
    factory = FakeAiFactory(FakeAiManager({}, answer))

    with mock.patch(_CHATBOT_FACTORY, factory):
        response = _CLIENT.post(
            "/chat",
            json={"conversation": [{"role": "user", "content": "hi"}]},
            headers=authorization(),
        )

    assert response.json() == {"answer": answer}


@settings(max_examples=25, deadline=None)
@given(st.text(min_size=1, max_size=10))
def test_chat_property_reports_a_model_it_cannot_reach(
    said: str,
) -> None:
    factory = FakeAiFactory(UnavailableAiManager())

    with mock.patch(_CHATBOT_FACTORY, factory):
        response = _CLIENT.post(
            "/chat",
            json={"conversation": [{"role": "user", "content": said}]},
            headers=authorization(),
        )

    assert response.status_code == _UNAVAILABLE
