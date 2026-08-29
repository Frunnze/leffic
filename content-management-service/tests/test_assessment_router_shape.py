import inspect
import uuid

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy.orm import Session, sessionmaker

from features.study_units import assessment_router
from features.study_units.assessment_router import (
    ReviewTestItemRequest,
    _upserted_review,
    review_test_item,
)
from shared.identifiers import RowId
from shared.models import TestItemReview
from tests.study_unit_access_support import (
    OK,
    UNPROCESSABLE,
    StudyUnitWorld,
    review_payload,
)
from tests.support import authorization

_CHOSEN_OPTION: list[object] = [0]
_CORRECT = 1
_NO_ANSWERS: list[object] = []
_ANY_ITEM_ID = 1


def test_upserted_review_creates_a_missing_row(
    sessions: sessionmaker[Session], world: StudyUnitWorld
) -> None:
    with sessions() as session:
        _upserted_review(
            session,
            world.test_session_id,
            world.test_item_id,
            _CHOSEN_OPTION,
            _CORRECT,
        )
        session.commit()

    with sessions() as session:
        stored = session.query(TestItemReview).one()

        assert stored.test_item_id == world.test_item_id
        assert stored.answers == _CHOSEN_OPTION
        assert stored.accuracy == _CORRECT


def test_owner_test_item_review_body_is_unchanged(
    client: TestClient, world: StudyUnitWorld
) -> None:
    response = client.post(
        "/review-test-item",
        json=review_payload(
            world.test_item_id, world.test_session_id, _CHOSEN_OPTION
        ),
        headers=authorization(str(world.owner)),
    )

    assert response.status_code == OK
    assert response.json() == {"msg": "Saved!"}


def test_review_test_item_stays_asynchronous() -> None:
    assert inspect.iscoroutinefunction(review_test_item)


def test_assessment_grading_class_is_gone() -> None:
    assert not hasattr(assessment_router, "AssessmentGrading")
    assert not hasattr(assessment_router, "_UNKNOWN_ITEM_ACCURACY")


def test_empty_answers_are_422_not_500(
    client: TestClient,
    sessions: sessionmaker[Session],
    world: StudyUnitWorld,
) -> None:
    response = client.post(
        "/review-test-item",
        json=review_payload(
            world.test_item_id, world.test_session_id, _NO_ANSWERS
        ),
        headers=authorization(str(world.owner)),
    )

    with sessions() as session:
        assert session.query(TestItemReview).count() == 0

    assert response.status_code == UNPROCESSABLE


def test_an_empty_answers_array_never_builds_a_review_request() -> None:
    with pytest.raises(ValidationError):
        _ = ReviewTestItemRequest.model_validate(
            review_payload(_ANY_ITEM_ID, uuid.uuid4(), _NO_ANSWERS)
        )


def test_a_single_answer_builds_a_review_request() -> None:
    parsed = ReviewTestItemRequest.model_validate(
        review_payload(_ANY_ITEM_ID, uuid.uuid4(), _CHOSEN_OPTION)
    )

    assert parsed.answers == _CHOSEN_OPTION


def test_review_request_field_types_are_unchanged() -> None:
    annotations = ReviewTestItemRequest.__annotations__

    assert annotations["test_item_id"] == RowId
    assert annotations["test_session"] is str
