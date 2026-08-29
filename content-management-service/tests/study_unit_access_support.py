import uuid
from typing import NamedTuple

from fastapi import HTTPException
from sqlalchemy.orm import Session, sessionmaker

from shared.models import Flashcard, TestItem, TestSession
from tests.assessment_seeding import seeded_test
from tests.property_support import seeded_deck

OK = 200
NOT_FOUND = 404
UNPROCESSABLE = 422
ABSENT_ROW_ID = 2**31 - 1
MISSING_FLASHCARD_DETAIL = "Flashcard does not exist!"
MISSING_TEST_ITEM_DETAIL = "Test item does not exist!"
ONGOING = "ongoing"


class StudyUnitWorld(NamedTuple):
    owner: uuid.UUID
    stranger: uuid.UUID
    flashcard_id: int
    test_item_id: int
    test_session_id: uuid.UUID


def seeded_world(sessions: sessionmaker[Session]) -> StudyUnitWorld:
    owner = uuid.uuid4()
    stranger = uuid.uuid4()

    with sessions() as session:
        _, _, card_ids = seeded_deck(session, owner, 1)
        _, test_id, item_ids = seeded_test(session, owner, 1)
        test_session_id = opened_test_session(session, owner, test_id)

    return StudyUnitWorld(
        owner=owner,
        stranger=stranger,
        flashcard_id=card_ids[0],
        test_item_id=item_ids[0],
        test_session_id=test_session_id,
    )


def opened_test_session(
    session: Session,
    user_id: uuid.UUID,
    origin_id: uuid.UUID,
    status: str = ONGOING,
) -> uuid.UUID:
    opened = TestSession(
        id=uuid.uuid4(),
        origin_id=origin_id,
        status=status,
        user_id=user_id,
    )
    session.add(opened)
    session.commit()

    return opened.id


def review_payload(
    test_item_id: int, test_session_id: uuid.UUID, answers: list[object]
) -> dict[str, object]:
    return {
        "test_item_id": test_item_id,
        "test_session": str(test_session_id),
        "answers": answers,
    }


def refusing_flashcard_lookup(
    _db: Session, _user_id: str, _flashcard_id: int
) -> Flashcard:
    raise HTTPException(
        status_code=NOT_FOUND, detail=MISSING_FLASHCARD_DETAIL
    )


def refusing_item_lookup(
    _db: Session, _user_id: str, _test_item_id: int
) -> TestItem:
    raise HTTPException(
        status_code=NOT_FOUND, detail=MISSING_TEST_ITEM_DETAIL
    )
