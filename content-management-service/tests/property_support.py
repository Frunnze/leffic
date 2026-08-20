import uuid
from datetime import UTC, datetime

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session, sessionmaker

from shared.models import File, Flashcard, FlashcardDeck, Folder
from tests.access_support import _wired_app
from tests.support import in_memory_sessions


def property_world() -> tuple[TestClient, sessionmaker[Session]]:
    sessions = in_memory_sessions()
    client = TestClient(_wired_app(sessions), raise_server_exceptions=False)

    return client, sessions


def seeded_deck(
    session: Session,
    owner: uuid.UUID,
    card_count: int,
    next_review: datetime | None = None,
) -> tuple[uuid.UUID, uuid.UUID, list[int]]:
    folder_id = uuid.uuid4()
    session.add(
        Folder(
            id=folder_id,
            name="Home",
            user_id=owner,
            created_at=datetime.now(UTC),
            public=False,
        )
    )
    session.flush()

    deck = FlashcardDeck(
        id=uuid.uuid4(),
        name="Deck",
        folder_id=folder_id,
        created_at=datetime.now(UTC),
        public=False,
    )
    session.add(deck)

    for index in range(card_count):
        deck.flashcards.append(
            Flashcard(
                type="basic",
                content={"front": f"q{index}"},
                next_review=next_review,
                created_at=datetime.now(UTC),
            )
        )

    session.commit()

    return folder_id, deck.id, [card.id for card in deck.flashcards]


def seeded_file(
    session: Session, owner: uuid.UUID, bookmarked_page: int | None = None
) -> uuid.UUID:
    folder_id = uuid.uuid4()
    session.add(
        Folder(
            id=folder_id,
            name="Home",
            user_id=owner,
            created_at=datetime.now(UTC),
            public=False,
        )
    )
    session.flush()

    file_id = uuid.uuid4()
    session.add(
        File(
            id=file_id,
            name="notes",
            folder_id=folder_id,
            created_at=datetime.now(UTC),
            public=False,
            extension="pdf",
            bookmarked_page=bookmarked_page,
        )
    )
    session.commit()

    return file_id
