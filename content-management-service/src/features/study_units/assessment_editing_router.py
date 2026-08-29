from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from features.study_units.study_unit_access import owned_test_item
from shared.dependencies import AuthenticatedUserId, DatabaseSession
from shared.identifiers import RowId

assessment_editing_router = APIRouter()


class UpdateTestItemRequest(BaseModel):
    test_item_id: RowId
    content: dict[str, object]


@assessment_editing_router.patch("/update-test-item")
async def update_test_item(
    request_data: UpdateTestItemRequest,
    user_id: AuthenticatedUserId,
    db: DatabaseSession,
) -> JSONResponse:
    item = owned_test_item(db, user_id, request_data.test_item_id)
    item.content = request_data.content
    db.commit()

    return JSONResponse(content={"msg": "Test item updated!"})
