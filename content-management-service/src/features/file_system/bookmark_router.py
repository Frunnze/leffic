from fastapi import APIRouter
from pydantic import BaseModel, Field

from features.file_system.file_access import owned_file
from shared.dependencies import AuthenticatedUserId, DatabaseSession

bookmark_router = APIRouter()


class BookmarkRequest(BaseModel):
    file_id: str
    page: int = Field(ge=1)


@bookmark_router.get("/file-bookmark")
async def get_file_bookmark(
    file_id: str, user_id: AuthenticatedUserId, db: DatabaseSession
) -> dict[str, int | None]:
    return {"page": owned_file(db, user_id, file_id).bookmarked_page}


@bookmark_router.put("/file-bookmark")
async def set_file_bookmark(
    request_data: BookmarkRequest,
    user_id: AuthenticatedUserId,
    db: DatabaseSession,
) -> dict[str, int | None]:
    file = owned_file(db, user_id, request_data.file_id)
    file.bookmarked_page = request_data.page
    db.commit()

    return {"page": file.bookmarked_page}


@bookmark_router.delete("/file-bookmark")
async def remove_file_bookmark(
    file_id: str, user_id: AuthenticatedUserId, db: DatabaseSession
) -> dict[str, int | None]:
    file = owned_file(db, user_id, file_id)
    file.bookmarked_page = None
    db.commit()

    return {"page": file.bookmarked_page}
