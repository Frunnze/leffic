import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from features.study_units import assessment_editing_router
from shared.models import TestItem
from tests.study_unit_access_support import (
    ABSENT_ROW_ID,
    MISSING_TEST_ITEM_DETAIL,
    NOT_FOUND,
    OK,
    StudyUnitWorld,
    refusing_item_lookup,
)
from tests.support import authorization

_NEW_CONTENT: dict[str, object] = {"question": "edited", "true_option": "y"}


def _updated(
    client: TestClient, test_item_id: int, user_id: str
) -> tuple[int, object]:
    response = client.patch(
        "/update-test-item",
        json={"test_item_id": test_item_id, "content": _NEW_CONTENT},
        headers=authorization(user_id),
    )

    return response.status_code, response.json()


def test_update_test_item_refuses_a_strangers_item_like_an_absent_one(
    client: TestClient, world: StudyUnitWorld
) -> None:
    stranger = _updated(
        client, world.test_item_id, str(world.stranger)
    )
    absent = _updated(client, ABSENT_ROW_ID, str(world.owner))

    assert stranger == absent
    assert stranger == (NOT_FOUND, {"detail": MISSING_TEST_ITEM_DETAIL})


def test_update_test_item_body_is_unchanged(
    client: TestClient, world: StudyUnitWorld
) -> None:
    answered = _updated(client, world.test_item_id, str(world.owner))

    assert answered == (OK, {"msg": "Test item updated!"})


def test_update_test_item_delegates_to_owned_test_item(
    client: TestClient,
    sessions: sessionmaker[Session],
    world: StudyUnitWorld,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        assessment_editing_router, "owned_test_item", refusing_item_lookup
    )
    status_code, _ = _updated(
        client, world.test_item_id, str(world.owner)
    )

    with sessions() as session:
        item = session.get(TestItem, world.test_item_id)

        assert item is not None
        assert item.content != _NEW_CONTENT

    assert status_code == NOT_FOUND


def test_assessment_editing_router_holds_no_ownership_detail() -> None:
    assert not hasattr(assessment_editing_router, "_MISSING_TEST_ITEM")
    assert not hasattr(assessment_editing_router, "Folder")
    assert hasattr(assessment_editing_router, "owned_test_item")
