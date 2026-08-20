from sqlalchemy.orm import Session

from features.study_units_generation.study_unit_source import (
    StudyUnitSource,
)
from features.study_units_generation.study_unit_writer import (
    PENDING_NAME,
    existing_folder,
    generated_records,
)
from shared.models import Test, TestItem

_MISSING_TEST = "Test does not exist!"


class MissingTestError(Exception):
    def __init__(self) -> None:
        super().__init__(_MISSING_TEST)


def _existing_test(db: Session, test_id: str) -> Test:
    test = db.query(Test).filter_by(id=test_id).first()

    if test is None:
        raise MissingTestError

    return test


def create_test(
    db: Session, folder_id: str, source: StudyUnitSource
) -> str:
    folder = existing_folder(db, folder_id)
    test = Test(
        folder_id=folder.id,
        name=PENDING_NAME,
        source_kind=source.kind,
        source_reference=source.reference,
    )
    db.add(test)
    db.commit()

    return str(test.id)


def append_test_items(
    db: Session, test_id: str, item_type: str, items: object
) -> int:
    test = _existing_test(db, test_id)
    appended = generated_records(items)

    for item in appended:
        test.test_items.append(TestItem(type=item_type, content=item))

    db.commit()

    return len(appended)


def name_test_once(db: Session, test_id: str, test_name: str) -> bool:
    named = (
        db.query(Test)
        .filter(Test.id == test_id, Test.name == PENDING_NAME)
        .update({Test.name: test_name})
    )
    db.commit()

    return bool(named)
