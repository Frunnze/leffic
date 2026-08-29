
from fastapi.testclient import TestClient

from tests.study_unit_access_support import (
    ABSENT_ROW_ID,
    NOT_FOUND,
    StudyUnitWorld,
)
from tests.support import authorization


def test_update_flashcard_refuses_a_stranger_like_an_absent_card(
    client: TestClient, world: StudyUnitWorld
) -> None:
    stranger = client.patch(
        "/update-flashcard",
        json={"flashcard_id": world.flashcard_id, "content": {"a": "b"}},
        headers=authorization(str(world.stranger)),
    )
    absent = client.patch(
        "/update-flashcard",
        json={"flashcard_id": ABSENT_ROW_ID, "content": {"a": "b"}},
        headers=authorization(str(world.owner)),
    )

    assert stranger.status_code == NOT_FOUND
    assert stranger.json() == absent.json()


def test_delete_flashcard_refuses_a_stranger_like_an_absent_card(
    client: TestClient, world: StudyUnitWorld
) -> None:
    stranger = client.delete(
        "/delete-flashcard/",
        params={"flashcard_id": world.flashcard_id},
        headers=authorization(str(world.stranger)),
    )
    absent = client.delete(
        "/delete-flashcard/",
        params={"flashcard_id": ABSENT_ROW_ID},
        headers=authorization(str(world.owner)),
    )

    assert stranger.status_code == NOT_FOUND
    assert stranger.json() == absent.json()
