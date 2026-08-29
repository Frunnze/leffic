import uuid
from typing import cast

import pytest
from sqlalchemy.exc import IntegrityError

from shared.models import TestSession
from shared.models.columns import FlexibleUuid
from tests.session_ownership_support import ONGOING
from tests.support import in_memory_sessions

_EXPECTED_COLUMNS = {
    "id",
    "origin_id",
    "status",
    "created_at",
    "user_id",
}


def test_user_id_column_is_non_nullable_uuid() -> None:
    column = TestSession.__table__.c.user_id

    assert cast("bool | None", column.nullable) is False
    assert isinstance(column.type, FlexibleUuid)


def test_a_session_without_a_user_is_rejected() -> None:
    sessions = in_memory_sessions()

    with sessions() as session:
        session.add(
            TestSession(origin_id=uuid.uuid4(), status=ONGOING)
        )

        with pytest.raises(IntegrityError):
            session.commit()


def test_session_columns_are_exactly_the_expected_set() -> None:
    column_names = set(TestSession.__table__.c.keys())

    assert column_names == _EXPECTED_COLUMNS
