from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from shared.dependencies import AuthenticatedUserId, DatabaseSession
from shared.models import Folder, Test, TestItem

assessment_editing_router = APIRouter()

_MISSING_TEST_ITEM = "Test item does not exist!"


class UpdateTestItemRequest(BaseModel):
    test_item_id: int
    content: dict[str, object]


@assessment_editing_router.patch("/update-test-item")
async def update_test_item(
    request_data: UpdateTestItemRequest,
    user_id: AuthenticatedUserId,
    db: DatabaseSession,
) -> JSONResponse:
    item = (
        db.query(TestItem)
        .join(Test)
        .join(Folder)
        .filter(
            TestItem.id == request_data.test_item_id,
            Folder.user_id == user_id,
        )
        .first()
    )

    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=_MISSING_TEST_ITEM
        )

    item.content = request_data.content
    db.commit()

    return JSONResponse(content={"msg": "Test item updated!"})
