import uuid
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from shared.models import File, FlashcardDeck, Folder, Note, Test
from tests.access_support import (
    HOME_ID,
    MISSING_DECK,
    MISSING_FILE,
    MISSING_TEST,
    MISSING_UNIT,
    OTHER_HOME_ID,
    OwnedContent,
    ScopedRoute,
    scoped_client,
    seeded_content,
    surviving_ids,
    unit_identifier,
)
from tests.support import authorization, in_memory_sessions

_TWIN_ID = uuid.UUID(int=0x5EED)
_FOREIGN_ROUTES = (
    ScopedRoute(
        "DELETE", "/delete-deck/", "deck_id", "deck_id", MISSING_UNIT
    ),
    ScopedRoute(
        "DELETE", "/delete-test/", "test_id", "test_id", MISSING_UNIT
    ),
    ScopedRoute(
        "DELETE", "/delete-file/", "file_id", "file_id", MISSING_FILE
    ),
    ScopedRoute(
        "GET", "/flashcards", "flashcard_deck_id", "deck_id", MISSING_DECK
    ),
    ScopedRoute("GET", "/test-items", "test_id", "test_id", MISSING_TEST),
)


@pytest.fixture
def sessions() -> sessionmaker[Session]:
    return in_memory_sessions()


@pytest.fixture
def client(sessions: sessionmaker[Session]) -> Iterator[TestClient]:
    yield from scoped_client(sessions)


@pytest.fixture
def owned(sessions: sessionmaker[Session]) -> OwnedContent:
    return seeded_content(sessions, HOME_ID)


@pytest.fixture
def twins(
    sessions: sessionmaker[Session], owned: OwnedContent
) -> OwnedContent:
    theirs = seeded_content(sessions, OTHER_HOME_ID)
    their_folder = uuid.UUID(theirs.folder_id)

    with sessions() as session:
        session.add(
            Note(
                id=_TWIN_ID,
                folder_id=uuid.UUID(owned.folder_id),
                name="Mine",
                content="mine",
                type="general",
            )
        )
        session.add_all(
            [
                FlashcardDeck(
                    id=_TWIN_ID, folder_id=their_folder, name="Theirs"
                ),
                Test(id=_TWIN_ID, folder_id=their_folder, name="Theirs"),
                File(
                    id=_TWIN_ID,
                    folder_id=their_folder,
                    name="theirs",
                    extension="pdf",
                ),
            ]
        )
        session.commit()

    return theirs


@pytest.mark.parametrize("route", _FOREIGN_ROUTES)
def test_a_twin_id_you_own_elsewhere_unlocks_nothing(
    client: TestClient, twins: OwnedContent, route: ScopedRoute
) -> None:
    assert unit_identifier(twins, route.attribute)

    response = client.request(
        route.method,
        route.path,
        params={route.parameter: str(_TWIN_ID)},
        headers=authorization(),
    )

    assert response.status_code == 404
    assert response.json() == {"detail": route.detail}


def test_a_twin_id_leaves_every_foreign_row_intact(
    client: TestClient, sessions: sessionmaker[Session], twins: OwnedContent
) -> None:
    for route in _FOREIGN_ROUTES:
        _ = client.request(
            route.method,
            route.path,
            params={route.parameter: str(_TWIN_ID)},
            headers=authorization(),
        )

    assert str(_TWIN_ID) in surviving_ids(sessions, FlashcardDeck)
    assert str(_TWIN_ID) in surviving_ids(sessions, Test)
    assert str(_TWIN_ID) in surviving_ids(sessions, File)
    assert twins.deck_id in surviving_ids(sessions, FlashcardDeck)


def test_a_twin_id_still_resolves_to_the_unit_you_own(
    client: TestClient, twins: OwnedContent
) -> None:
    assert twins.note_id

    response = client.get(
        "/note",
        params={"note_id": str(_TWIN_ID)},
        headers=authorization(),
    )

    assert response.status_code == 200
    assert response.json() == {
        "content": "mine",
        "name": "Mine",
        "read": False,
    }


def test_a_folder_you_own_is_never_a_deck_you_do_not(
    client: TestClient, sessions: sessionmaker[Session], owned: OwnedContent
) -> None:
    theirs = seeded_content(sessions, OTHER_HOME_ID)
    twin = uuid.UUID(int=0xF01DE4)

    with sessions() as session:
        session.add(
            Folder(id=twin, parent_id=HOME_ID, name="T", user_id=HOME_ID)
        )
        session.add(
            FlashcardDeck(
                id=twin,
                folder_id=uuid.UUID(theirs.folder_id),
                name="Theirs",
            )
        )
        session.commit()

    response = client.request(
        "DELETE",
        "/delete-deck/",
        params={"deck_id": str(twin)},
        headers=authorization(),
    )

    assert response.status_code == 404
    assert str(twin) in surviving_ids(sessions, FlashcardDeck)
    assert owned.deck_id in surviving_ids(sessions, FlashcardDeck)
