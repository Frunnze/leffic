import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Query, Session

from features.study_units.formatting import (
    date_to_str,
    evaluate_accuracy,
    prepare_content,
)
from shared.content_access import owned_content
from shared.dependencies import AuthenticatedUserId, DatabaseSession
from shared.folder_tree import subfolder_ids
from shared.models import (
    Test,
    TestItem,
    TestItemReview,
    TestSession,
)

assessment_router = APIRouter()

_HOME_FOLDER = "home"
_DEFAULT_PER_PAGE = 10
_FIRST_PAGE = 1
_ONGOING = "ongoing"
_MISSING_ORIGIN = "Test or folder is required!"
_UNKNOWN_ITEM_ACCURACY = 0
_MISSING_TEST = "Test does not exist!"


def _session_answers(
    test_item: TestItem, db: Session, test_session: str
) -> list[object] | None:
    review = (
        db.query(TestItemReview)
        .filter(
            TestItemReview.test_session == test_session,
            TestItemReview.test_item_id == test_item.id,
        )
        .first()
    )

    return review.answers if review else None


def _ongoing_session(db: Session, origin_id: str) -> str:
    existing = (
        db.query(TestSession)
        .filter(
            TestSession.origin_id == origin_id,
            TestSession.status == _ONGOING,
        )
        .first()
    )

    if existing:
        return str(existing.id)

    new_session = TestSession(origin_id=origin_id, status=_ONGOING)
    db.add(new_session)
    db.commit()

    return str(new_session.id)


def _test_items_query(
    db: Session, test_id: str | None, folder_id: str, user_id: str
) -> Query[TestItem]:
    if test_id:
        return db.query(TestItem).filter(
            TestItem.test_id == uuid.UUID(test_id)
        )

    test_ids = select(Test.id).where(
        Test.folder_id.in_(subfolder_ids(folder_id, user_id))
    )

    return db.query(TestItem).filter(TestItem.test_id.in_(test_ids))


@assessment_router.get("/test-items")
async def get_test_items(
    user_id: AuthenticatedUserId,
    db: DatabaseSession,
    *,
    test_id: str | None = None,
    folder_id: str | None = None,
    per_page: int = _DEFAULT_PER_PAGE,
    page: int = _FIRST_PAGE,
    test_session: str | None = None,
) -> JSONResponse:
    if test_id:
        _ = owned_content(db, user_id, Test, test_id, _MISSING_TEST)

    resolved_folder_id = user_id if folder_id == _HOME_FOLDER else folder_id
    origin_id = test_id or resolved_folder_id

    if origin_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=_MISSING_ORIGIN
        )

    # Check if this origin has any unfinished test session
    if not test_session:
        test_session = _ongoing_session(db, origin_id)

    items_query = _test_items_query(
        db, test_id, resolved_folder_id or origin_id, user_id
    )
    test_items = (
        items_query.offset((page - 1) * per_page).limit(per_page).all()
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
                    "last_answers": _session_answers(
                        test_item, db, test_session
                    ),
                }
                for test_item in test_items
            ],
            "total_items": items_query.count(),
            "test_session": test_session,
            "page": page,
            "per_page": per_page,
        }
    )


class AssessmentGrading:
    @staticmethod
    def graded(test_item: TestItem | None, answers: list[object]) -> int:
        if test_item is None:
            return _UNKNOWN_ITEM_ACCURACY

        return evaluate_accuracy(
            answers, test_item.type, test_item.content
        )


class ReviewTestItemRequest(BaseModel):
    test_item_id: int
    test_session: str
    answers: list[object]


@assessment_router.post("/review-test-item")
async def review_test_item(
    req_data: ReviewTestItemRequest, db: DatabaseSession
) -> JSONResponse:
    review = (
        db.query(TestItemReview)
        .filter(
            TestItemReview.test_item_id == req_data.test_item_id,
            TestItemReview.test_session == req_data.test_session,
        )
        .first()
    )

    if not review:
        db.add(
            TestItemReview(
                test_session=uuid.UUID(req_data.test_session),
                test_item_id=req_data.test_item_id,
                accuracy=AssessmentGrading.graded(
                    db.get(TestItem, req_data.test_item_id),
                    req_data.answers,
                ),
                answers=req_data.answers,
                reviewed_at=datetime.now(UTC),
            )
        )
    else:
        review.answers = req_data.answers
        review.reviewed_at = datetime.now(UTC)
        review.accuracy = AssessmentGrading.graded(
            db.get(TestItem, req_data.test_item_id),
            req_data.answers,
        )

    db.commit()

    return JSONResponse(content={"msg": "Saved!"})
