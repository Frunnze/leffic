import uuid
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from features.study_units.assessment_queries import (
    MISSING_SESSION,
    MISSING_TEST,
    items_query,
    ongoing_session,
    owned_scope,
    session_answers,
)
from features.study_units.formatting import (
    date_to_str,
    evaluate_accuracy,
    prepare_content,
)
from features.study_units.study_unit_access import owned_test_item
from shared.content_access import owned_content
from shared.dependencies import AuthenticatedUserId, DatabaseSession
from shared.identifiers import RowId, parsed_identifier
from shared.models import (
    Test,
    TestItemReview,
)

assessment_router = APIRouter()

_DEFAULT_PER_PAGE = 10
_FIRST_PAGE = 1
_MISSING_ORIGIN = "Test or folder is required!"


class TestItemsQuery(BaseModel):
    test_id: str | None = None
    folder_id: str | None = None
    per_page: int = _DEFAULT_PER_PAGE
    page: int = _FIRST_PAGE
    test_session: str | None = None


@assessment_router.get("/test-items")
async def get_test_items(
    user_id: AuthenticatedUserId,
    db: DatabaseSession,
    query: Annotated[TestItemsQuery, Depends()],
) -> JSONResponse:
    if query.test_id:
        _ = owned_content(db, user_id, Test, query.test_id, MISSING_TEST)

    resolved_folder_id = owned_scope(user_id, query.folder_id)
    origin_id = query.test_id or resolved_folder_id

    if origin_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=_MISSING_ORIGIN
        )

    # Check if this origin has any unfinished test session
    test_session = query.test_session
    if not test_session:
        test_session = ongoing_session(db, origin_id)

    matching_items = items_query(
        db, query.test_id, resolved_folder_id or origin_id, user_id
    )
    test_items = (
        matching_items.offset((query.page - 1) * query.per_page)
        .limit(query.per_page)
        .all()
    )

    return JSONResponse(
        content={
            "test_items": [
                {
                    "id": test_item.id,
                    "type": test_item.type,
                    "content": prepare_content(
                        test_item.content, test_item.type
                    ),
                    "created_at": date_to_str(test_item.created_at),
                    "last_answers": session_answers(
                        test_item, db, test_session
                    ),
                }
                for test_item in test_items
            ],
            "total_items": matching_items.count(),
            "test_session": test_session,
            "page": query.page,
            "per_page": query.per_page,
        }
    )


class ReviewTestItemRequest(BaseModel):
    test_item_id: RowId
    test_session: str
    answers: Annotated[list[object], Field(min_length=1)]


def _upserted_review(
    db: Session,
    session_id: uuid.UUID,
    item_id: int,
    answers: list[object],
    accuracy: int,
) -> None:
    review = (
        db.query(TestItemReview)
        .filter(
            TestItemReview.test_item_id == item_id,
            TestItemReview.test_session == session_id,
        )
        .first()
    )

    if review is None:
        db.add(
            TestItemReview(
                test_session=session_id,
                test_item_id=item_id,
                accuracy=accuracy,
                answers=answers,
                reviewed_at=datetime.now(UTC),
            )
        )

        return

    review.answers = answers
    review.reviewed_at = datetime.now(UTC)
    review.accuracy = accuracy


@assessment_router.post("/review-test-item")
async def review_test_item(
    request_data: ReviewTestItemRequest,
    db: DatabaseSession,
    user_id: AuthenticatedUserId,
) -> JSONResponse:
    session_id = parsed_identifier(request_data.test_session, MISSING_SESSION)
    item = owned_test_item(db, user_id, request_data.test_item_id)
    accuracy = evaluate_accuracy(
        request_data.answers, item.type, item.content
    )

    _upserted_review(
        db, session_id, item.id, request_data.answers, accuracy
    )
    db.commit()

    return JSONResponse(content={"msg": "Saved!"})
