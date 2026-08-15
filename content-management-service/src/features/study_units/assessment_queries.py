from sqlalchemy import select
from sqlalchemy.orm import Query, Session

from shared.folder_access import MISSING_FOLDER
from shared.folder_tree import subfolder_ids
from shared.identifiers import parsed_identifier
from shared.models import Test, TestItem, TestItemReview, TestSession

HOME_FOLDER = "home"
MISSING_TEST = "Test does not exist!"
MISSING_SESSION = "Test session does not exist!"

_ONGOING = "ongoing"


def owned_scope(user_id: str, folder_id: str | None) -> str | None:
    if folder_id is None:
        return None

    if folder_id == HOME_FOLDER:
        return user_id

    _ = parsed_identifier(folder_id, MISSING_FOLDER)

    return folder_id


def session_answers(
    test_item: TestItem, db: Session, test_session: str
) -> list[object] | None:
    review = (
        db.query(TestItemReview)
        .filter(
            TestItemReview.test_session
            == parsed_identifier(test_session, MISSING_SESSION),
            TestItemReview.test_item_id == test_item.id,
        )
        .first()
    )

    return review.answers if review else None


def ongoing_session(db: Session, origin_id: str) -> str:
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


def items_query(
    db: Session, test_id: str | None, folder_id: str, user_id: str
) -> Query[TestItem]:
    if test_id:
        return db.query(TestItem).filter(
            TestItem.test_id == parsed_identifier(
                test_id, MISSING_TEST
            )
        )

    test_ids = select(Test.id).where(
        Test.folder_id.in_(subfolder_ids(folder_id, user_id))
    )

    return db.query(TestItem).filter(TestItem.test_id.in_(test_ids))
