from typing import cast

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import case, func

from src.shared.dependencies import AuthenticatedUserId, DatabaseSession
from src.shared.folder_tree import subfolder_ids
from src.shared.models import Test, TestItem, TestItemReview, TestSession

assessment_stats_router = APIRouter()

_HOME_FOLDER = "home"
_DONE = "done"
_NO_TEST_STATS = "No test stats!"
_CORRECT_ACCURACY = 0.9
_FULLY_CORRECT = 1.0


@assessment_stats_router.get("/test-items-stats")
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


@assessment_stats_router.get("/test-session-results")
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
