from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from features.file_system.file_storage import delete_file_from_storage
from shared.dependencies import DatabaseSession
from shared.models import File, FlashcardDeck, Folder, Note, Test

content_router = APIRouter()


class FileMetadata(BaseModel):
    file_id: str
    name: str
    extension: str


class SaveFileNamesRequest(BaseModel):
    file_metadata: list[FileMetadata]
    folder_id: str | None = None


@content_router.post("/save-file-names")
async def save_file_names(
    request_data: SaveFileNamesRequest, db: DatabaseSession
) -> JSONResponse:
    folder = db.query(Folder).filter_by(id=request_data.folder_id).first()

    if not folder:
        folder = Folder(name=request_data.file_metadata[0].name)

    for file_meta in request_data.file_metadata:
        folder.files.append(
            File(
                id=file_meta.file_id,
                name=file_meta.name,
                extension=file_meta.extension,
            )
        )

    db.commit()

    return JSONResponse(content={"msg": "File names saved!"})


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
