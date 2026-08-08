from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from src.shared.dependencies import AuthenticatedUserId, DatabaseSession
from src.shared.folder_tree import subfolder_ids
from src.shared.models import Folder, Note

note_router = APIRouter()

_HOME_FOLDER = "home"
_NO_NOTES = "No notes!"
_MISSING_FOLDER = "Folder does not exist!"
_MISSING_NOTE = "Note does not exist!"


@note_router.get("/note")
async def get_note(note_id: str, db: DatabaseSession) -> JSONResponse:
    note = db.query(Note).filter(Note.id == note_id).first()

    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=_MISSING_NOTE
        )

    if not note.read:
        note.read = True
        db.commit()

    return JSONResponse(content={"content": note.content, "name": note.name})


@note_router.get("/notes-stats")
async def get_notes_stats(
    user_id: AuthenticatedUserId,
    db: DatabaseSession,
    folder_id: str | None = None,
) -> JSONResponse:
    resolved_folder_id = user_id if folder_id == _HOME_FOLDER else folder_id

    user_folder_exists = (
        db.query(Folder)
        .filter(Folder.user_id == user_id, Folder.id == resolved_folder_id)
        .first()
    )

    if not user_folder_exists or resolved_folder_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=_MISSING_FOLDER
        )

    folder_ids = subfolder_ids(resolved_folder_id, user_id)
    due_notes = (
        db.query(Note)
        .filter(Note.folder_id.in_(folder_ids), Note.read.is_(False))
        .count()
    )
    read_notes = (
        db.query(Note)
        .filter(Note.folder_id.in_(folder_ids), Note.read.is_(True))
        .count()
    )

    if read_notes == 0 and due_notes == 0:
        return JSONResponse(
            content={"msg": _NO_NOTES},
            status_code=status.HTTP_404_NOT_FOUND,
        )

    return JSONResponse(content={"due": due_notes, "read": read_notes})
