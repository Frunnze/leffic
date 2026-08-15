from fastapi import APIRouter
from fastapi.responses import JSONResponse

from features.file_system.file_access import owned_file
from shared.content_access import owned_content
from shared.dependencies import AuthenticatedUserId, DatabaseSession
from shared.file_storage import delete_file_from_storage
from shared.models import FlashcardDeck, Note, Test

content_router = APIRouter()

_MISSING_UNIT = "Unit does not exist!"


@content_router.delete("/delete-deck/")
async def delete_deck(
    deck_id: str, user_id: AuthenticatedUserId, db: DatabaseSession
) -> JSONResponse:
    deck = owned_content(
        db, user_id, FlashcardDeck, deck_id, _MISSING_UNIT
    )

    db.delete(deck)
    db.commit()

    return JSONResponse(content={"msg": "Deck deleted!"})


@content_router.delete("/delete-test/")
async def delete_test(
    test_id: str, user_id: AuthenticatedUserId, db: DatabaseSession
) -> JSONResponse:
    test = owned_content(db, user_id, Test, test_id, _MISSING_UNIT)

    db.delete(test)
    db.commit()

    return JSONResponse(content={"msg": "Test deleted!"})


@content_router.delete("/delete-note/")
async def delete_note(
    note_id: str, user_id: AuthenticatedUserId, db: DatabaseSession
) -> JSONResponse:
    note = owned_content(db, user_id, Note, note_id, _MISSING_UNIT)

    db.delete(note)
    db.commit()

    return JSONResponse(content={"msg": "Note deleted!"})


@content_router.delete("/delete-file/")
async def delete_file(
    file_id: str, user_id: AuthenticatedUserId, db: DatabaseSession
) -> JSONResponse:
    file = owned_file(db, user_id, file_id)
    file_storage_id = f"{file.id}.{file.extension}"

    db.delete(file)
    db.commit()
    delete_file_from_storage(file_storage_id)

    return JSONResponse(content={"msg": "File deleted!"})
