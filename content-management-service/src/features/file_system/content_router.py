from fastapi import APIRouter
from fastapi.responses import JSONResponse

from features.file_system.file_storage import delete_file_from_storage
from shared.dependencies import DatabaseSession
from shared.models import File, FlashcardDeck, Note, Test

content_router = APIRouter()


@content_router.delete("/delete-deck/")
async def delete_deck(deck_id: str, db: DatabaseSession) -> JSONResponse:
    db.delete(db.query(FlashcardDeck).filter_by(id=deck_id).first())
    db.commit()

    return JSONResponse(content={"msg": "Deck deleted!"})


@content_router.delete("/delete-test/")
async def delete_test(test_id: str, db: DatabaseSession) -> JSONResponse:
    db.delete(db.query(Test).filter_by(id=test_id).first())
    db.commit()

    return JSONResponse(content={"msg": "Test deleted!"})


@content_router.delete("/delete-note/")
async def delete_note(note_id: str, db: DatabaseSession) -> JSONResponse:
    db.delete(db.query(Note).filter_by(id=note_id).first())
    db.commit()

    return JSONResponse(content={"msg": "Note deleted!"})


@content_router.delete("/delete-file/")
async def delete_file(file_id: str, db: DatabaseSession) -> JSONResponse:
    file = db.query(File).filter_by(id=file_id).first()

    if file is None:
        return JSONResponse(
            status_code=404, content={"detail": "File not found"}
        )

    file_storage_id = f"{file.id}.{file.extension}"
    db.delete(file)
    db.commit()
    delete_file_from_storage(file_storage_id)

    return JSONResponse(content={"msg": "File deleted!"})
