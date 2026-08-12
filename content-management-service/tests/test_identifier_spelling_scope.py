from collections.abc import Iterator
from typing import cast

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from shared.models import File, FlashcardDeck, Note, Test
from tests.access_support import (
    HOME_ID,
    MISSING_DECK,
    MISSING_FILE,
    MISSING_FOLDER,
    MISSING_NOTE,
    MISSING_TEST,
    MISSING_UNIT,
    OTHER_HOME_ID,
    OwnedContent,
    ScopedRoute,
    identifier_spellings,
    opened_test_sessions,
    scoped_client,
    seeded_content,
    surviving_folder_ids,
    surviving_ids,
    unit_identifier,
)
from tests.support import OTHER_USER_ID, authorization, in_memory_sessions

_SCOPED_ROUTES = (
    ScopedRoute(
        "DELETE", "/delete-deck/", "deck_id", "deck_id", MISSING_UNIT
    ),
    ScopedRoute(
        "DELETE", "/delete-test/", "test_id", "test_id", MISSING_UNIT
    ),
    ScopedRoute(
        "DELETE", "/delete-note/", "note_id", "note_id", MISSING_UNIT
    ),
    ScopedRoute(
        "DELETE", "/delete-file/", "file_id", "file_id", MISSING_FILE
    ),
    ScopedRoute(
        "DELETE",
        "/delete-folder/",
        "folder_id",
        "folder_id",
        MISSING_FOLDER,
    ),
    ScopedRoute("GET", "/note", "note_id", "note_id", MISSING_NOTE),
    ScopedRoute(
        "GET", "/flashcards", "flashcard_deck_id", "deck_id", MISSING_DECK
    ),
    ScopedRoute("GET", "/test-items", "test_id", "test_id", MISSING_TEST),
)
_STABLE_READ_ROUTES = (
    ("/note", "note_id", "note_id"),
    ("/flashcards", "flashcard_deck_id", "deck_id"),
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
def intruder(sessions: sessionmaker[Session]) -> dict[str, str]:
    _ = seeded_content(sessions, OTHER_HOME_ID)

    return authorization(OTHER_USER_ID)


def _test_items_summary(
    client: TestClient, test_id: str
) -> tuple[int, object, object, tuple[object, ...]]:
    response = client.get(
        "/test-items",
        params={"test_id": test_id},
        headers=authorization(),
    )
    body = cast("dict[str, object]", response.json())
    items = cast("list[dict[str, object]]", body["test_items"])

    return (
        response.status_code,
        body["test_session"],
        body["total_items"],
        tuple(item["id"] for item in items),
    )


@pytest.mark.parametrize("route", _SCOPED_ROUTES)
def test_no_spelling_of_a_foreign_id_is_ever_accepted(
    client: TestClient,
    owned: OwnedContent,
    intruder: dict[str, str],
    route: ScopedRoute,
) -> None:
    unit_id = unit_identifier(owned, route.attribute)

    for spelling in identifier_spellings(unit_id):
        response = client.request(
            route.method,
            route.path,
            params={route.parameter: spelling},
            headers=intruder,
        )

        assert response.status_code == 404
        assert response.json() == {"detail": route.detail}


def test_no_spelling_of_a_foreign_id_destroys_a_row(
    client: TestClient,
    sessions: sessionmaker[Session],
    owned: OwnedContent,
    intruder: dict[str, str],
) -> None:
    for route in _SCOPED_ROUTES:
        unit_id = unit_identifier(owned, route.attribute)
        spellings = identifier_spellings(unit_id)

        for spelling in spellings:
            _ = client.request(
                route.method,
                route.path,
                params={route.parameter: spelling},
                headers=intruder,
            )

    assert owned.deck_id in surviving_ids(sessions, FlashcardDeck)
    assert owned.test_id in surviving_ids(sessions, Test)
    assert owned.note_id in surviving_ids(sessions, Note)
    assert owned.file_id in surviving_ids(sessions, File)
    assert owned.folder_id in surviving_folder_ids(sessions)


@pytest.mark.parametrize(
    ("path", "parameter", "attribute"), _STABLE_READ_ROUTES
)
def test_every_spelling_of_an_owned_id_reads_alike(
    client: TestClient,
    owned: OwnedContent,
    path: str,
    parameter: str,
    attribute: str,
) -> None:
    spellings = identifier_spellings(unit_identifier(owned, attribute))
    answers = [
        client.get(
            path, params={parameter: spelling}, headers=authorization()
        ).json()
        for spelling in spellings
    ]

    assert answers.count(answers[0]) == len(answers)


def test_every_spelling_of_an_owned_test_shares_one_session(
    client: TestClient, sessions: sessionmaker[Session], owned: OwnedContent
) -> None:
    answers = [
        _test_items_summary(client, spelling)
        for spelling in identifier_spellings(owned.test_id)
    ]

    assert answers.count(answers[0]) == len(answers)
    assert opened_test_sessions(sessions) == 1
