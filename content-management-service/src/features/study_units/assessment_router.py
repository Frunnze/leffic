import uuid
from datetime import UTC, datetime
from typing import cast

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import case, func, select
from sqlalchemy.orm import Query, Session

from src.features.study_units.formatting import (
    date_to_str,
    evaluate_accuracy,
    prepare_content,
)
from src.shared.dependencies import AuthenticatedUserId, DatabaseSession
from src.shared.folder_tree import subfolder_ids
from src.shared.models import (
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
_DONE = "done"
_NO_TEST_STATS = "No test stats!"
_MISSING_ORIGIN = "Test or folder is required!"
_CORRECT_ACCURACY = 0.9
_FULLY_CORRECT = 1.0


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
                    "content": prepare_content(test_item.content),
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
                accuracy=evaluate_accuracy(req_data.answers),
                answers=req_data.answers,
                reviewed_at=datetime.now(UTC),
            )
        )
    else:
        review.answers = req_data.answers
        review.reviewed_at = datetime.now(UTC)
        review.accuracy = evaluate_accuracy(req_data.answers)

    db.commit()

    return JSONResponse(content={"msg": "Saved!"})


@assessment_router.get("/test-items-stats")
async def test_items_stats(
    folder_id: str, db: DatabaseSession, user_id: AuthenticatedUserId
) -> JSONResponse:
    resolved_folder_id = user_id if folder_id == _HOME_FOLDER else folder_id

    # Recursive CTE to get all subfolder IDs
    folder_ids = subfolder_ids(resolved_folder_id, user_id)
    total_items = (
        db.query(TestItem)
        .join(Test, Test.id == TestItem.test_id)
        .filter(Test.folder_id.in_(folder_ids))
        .count()
    )

    average_accuracy = (
        db.query(
            TestItemReview.test_item_id.label("test_item_id"),
            func.avg(TestItemReview.accuracy).label("avg_accuracy"),
        )
        .join(TestItem, TestItem.id == TestItemReview.test_item_id)
        .join(Test, Test.id == TestItem.test_id)
        .filter(TestItemReview.accuracy.is_not(None))
        .filter(Test.folder_id.in_(folder_ids))
        .group_by(TestItemReview.test_item_id)
        .subquery()
    )
    correct_items = (
        db.query(average_accuracy)
        .filter(average_accuracy.c.avg_accuracy >= _CORRECT_ACCURACY)
        .count()
    )

    if total_items > 0:
        return JSONResponse(
            content={"total": total_items, "correct": correct_items}
        )

    return JSONResponse(
        content={"msg": _NO_TEST_STATS},
        status_code=status.HTTP_404_NOT_FOUND,
    )


@assessment_router.get("/test-session-results")
async def test_session_results(
    test_session: str, db: DatabaseSession
) -> JSONResponse:
    correct = cast(
        "int | None",
        db.query(
            func.sum(
                case((TestItemReview.accuracy == _FULLY_CORRECT, 1), else_=0)
            )
        )
        .filter(
            TestItemReview.accuracy.is_not(None),
            TestItemReview.test_session == test_session,
        )
        .scalar(),
    )

    # End the test session
    session_row = (
        db.query(TestSession).filter_by(id=test_session).first()
    )

    if session_row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=_NO_TEST_STATS
        )

    session_row.status = _DONE
    db.commit()

    if correct:
        return JSONResponse(content={"correct": correct})

    return JSONResponse(
        content={"msg": _NO_TEST_STATS},
        status_code=status.HTTP_404_NOT_FOUND,
    )
