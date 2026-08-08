from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from shared.dependencies import DatabaseSession
from shared.models import (
    Flashcard,
    FlashcardDeck,
    Folder,
    Note,
    Test,
    TestItem,
)

study_unit_saving = APIRouter()

_FLASHCARDS_SUFFIX = "_flashcards"
_MISSING_FOLDER = "Folder does not exist!"


class FlashcardRequest(BaseModel):
    deck_name: str
    folder_id: str | None = None
    flashcards: dict[str, list[dict[str, object]]]


@study_unit_saving.post("/save-flashcards")
async def save_flashcards(
    request_data: FlashcardRequest, db: DatabaseSession
) -> JSONResponse:
    # Create or get folder
    folder = db.query(Folder).filter_by(id=request_data.folder_id).first()

    if folder is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=_MISSING_FOLDER
        )

    # Create flashcard deck
    flashcard_deck = FlashcardDeck(
        folder_id=folder.id, name=request_data.deck_name
    )
    db.add(flashcard_deck)

    # Save flashcards
    for flashcard_type, flashcards in request_data.flashcards.items():
        cleaned_type = flashcard_type.replace(_FLASHCARDS_SUFFIX, "")

        for flashcard in flashcards:
            flashcard_deck.flashcards.append(
                Flashcard(type=cleaned_type, content=flashcard)
            )

    db.commit()

    return JSONResponse(
        content={"flashcard_deck_id": str(flashcard_deck.id)}
    )


class SaveNoteRequest(BaseModel):
    note_content: str
    note_name: str
    folder_id: str | None = None


@study_unit_saving.post("/save-note")
async def save_note(
    request_data: SaveNoteRequest, db: DatabaseSession
) -> JSONResponse:
    new_note = Note(
        folder_id=request_data.folder_id,
        name=request_data.note_name,
        content=request_data.note_content,
        type="general",
    )
    db.add(new_note)
    db.commit()

    return JSONResponse(content={"note_id": str(new_note.id)})


class SaveTestRequest(BaseModel):
    test_name: str
    folder_id: str | None = None
    test_items: list[dict[str, object]]


@study_unit_saving.post("/save-test")
async def save_test(
    request_data: SaveTestRequest, db: DatabaseSession
) -> JSONResponse:
    new_test = Test(
        folder_id=request_data.folder_id, name=request_data.test_name
    )
    db.add(new_test)

    for test_item in request_data.test_items:
        new_test.test_items.append(
            TestItem(content=test_item, type="mult_choice")
        )

    db.commit()

    return JSONResponse(content={"test_id": str(new_test.id)})
