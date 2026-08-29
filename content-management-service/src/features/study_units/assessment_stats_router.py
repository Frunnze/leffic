import uuid
from typing import cast

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from features.study_units.session_access import owned_session
from shared.dependencies import AuthenticatedUserId, DatabaseSession
from shared.folder_access import resolved_folder_id as resolved_scope
from shared.folder_tree import subfolder_ids
from shared.models import Test, TestItem, TestItemReview

assessment_stats_router = APIRouter()

_DONE = "done"
_NO_TEST_STATS = "No test stats!"
_CORRECT_ACCURACY = 0.9
_FULLY_CORRECT = 1.0


@assessment_stats_router.get("/test-items-stats")
async def test_items_stats(
    folder_id: str, db: DatabaseSession, user_id: AuthenticatedUserId
) -> JSONResponse:
    resolved_folder_id = resolved_scope(user_id, folder_id)

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


def _count_correct_answers(
    db: Session, session_id: uuid.UUID
) -> int:
    correct_answer_count = cast(
        "int | None",
        db.query(
            func.sum(
                case(
                    (TestItemReview.accuracy == _FULLY_CORRECT, 1),
                    else_=0,
                )
            )
        )
        .filter(
            TestItemReview.accuracy.is_not(None),
            TestItemReview.test_session == session_id,
        )
        .scalar(),
    )

    return correct_answer_count or 0


@assessment_stats_router.get("/test-session-results")
async def test_session_results(
    test_session: str,
    db: DatabaseSession,
    user_id: AuthenticatedUserId,
) -> JSONResponse:
    session_row = owned_session(
        db, user_id, test_session, _NO_TEST_STATS
    )
    correct_answer_count = _count_correct_answers(db, session_row.id)

    # End the test session
    session_row.status = _DONE
    db.commit()

    if correct_answer_count:
        return JSONResponse(
            content={"correct": correct_answer_count}
        )

    return JSONResponse(
        content={"msg": _NO_TEST_STATS},
        status_code=status.HTTP_404_NOT_FOUND,
    )
