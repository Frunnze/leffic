from typing import NoReturn

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from features.study_units.study_unit_access import MISSING_TEST_ITEM
from shared.folder_tree import subfolder_ids
from shared.identifiers import parsed_identifier
from shared.models import Test, TestItem, TestSession


def _refuse(missing_detail: str) -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=missing_detail
    )


def owned_session(
    db: Session, user_id: str, session_id: str, missing_detail: str
) -> TestSession:
    session_row = (
        db.query(TestSession)
        .filter(
            TestSession.id
            == parsed_identifier(session_id, missing_detail),
            TestSession.user_id == user_id,
        )
        .first()
    )

    if session_row is None:
        _refuse(missing_detail)

    return session_row


def owned_session_for_origin(
    db: Session,
    user_id: str,
    session_id: str,
    origin_id: str,
    missing_detail: str,
) -> TestSession:
    session_row = owned_session(
        db, user_id, session_id, missing_detail
    )
    requested_origin_id = parsed_identifier(origin_id, missing_detail)

    if session_row.origin_id != requested_origin_id:
        _refuse(missing_detail)

    return session_row


def session_covering_item(
    db: Session, user_id: str, session_id: str, test_item: TestItem
) -> TestSession:
    session_row = owned_session(
        db, user_id, session_id, MISSING_TEST_ITEM
    )

    if session_row.origin_id == test_item.test_id:
        return session_row

    covering_test_id = (
        db.query(Test.id)
        .filter(
            Test.id == test_item.test_id,
            Test.folder_id.in_(
                subfolder_ids(str(session_row.origin_id), user_id)
            ),
        )
        .first()
    )

    if covering_test_id is None:
        _refuse(MISSING_TEST_ITEM)

    return session_row
