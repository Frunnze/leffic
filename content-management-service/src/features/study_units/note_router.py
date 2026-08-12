from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from shared.content_access import owned_content
from shared.dependencies import AuthenticatedUserId, DatabaseSession
from shared.folder_access import owned_folder_id
from shared.folder_tree import subfolder_ids
from shared.models import Note

note_router = APIRouter()

_NO_NOTES = "No notes!"
_MISSING_NOTE = "Note does not exist!"


@note_router.get("/note")
async def get_note(
    note_id: str, user_id: AuthenticatedUserId, db: DatabaseSession
) -> JSONResponse:
    note = owned_content(db, user_id, Note, note_id, _MISSING_NOTE)

    return JSONResponse(
        content={
            "content": note.content,
            "name": note.name,
            "read": note.read,
        }
    )


class ReviewNoteRequest(BaseModel):
    note_id: str


@note_router.post("/review-note")
async def review_note(
    request_data: ReviewNoteRequest,
    user_id: AuthenticatedUserId,
    db: DatabaseSession,
) -> JSONResponse:
    note = owned_content(
        db, user_id, Note, request_data.note_id, _MISSING_NOTE
    )

    note.read = True
    db.commit()

    return JSONResponse(content={"note_id": request_data.note_id})


@note_router.get("/notes-stats")
async def get_notes_stats(
    user_id: AuthenticatedUserId,
    db: DatabaseSession,
    folder_id: str | None = None,
) -> JSONResponse:
    resolved_folder_id = owned_folder_id(db, user_id, folder_id)

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
