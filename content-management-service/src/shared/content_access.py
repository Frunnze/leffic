from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from shared.identifiers import parsed_identifier
from shared.models import File, FlashcardDeck, Folder, Note, Test

type ContentUnit = FlashcardDeck | Test | Note | File
type ContentModel = type[ContentUnit]


def owned_content[UnitT: ContentUnit](
    db: Session,
    user_id: str,
    model: type[UnitT],
    unit_id: str,
    missing_detail: str,
) -> UnitT:
    unit = (
        db.query(model)
        .join(Folder)
        .filter(
            model.id == parsed_identifier(unit_id, missing_detail),
            Folder.user_id == user_id,
        )
        .first()
    )

    if unit is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=missing_detail
        )

    return unit
