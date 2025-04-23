from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import uuid
import traceback
from sqlalchemy.orm import Session

from ..models import Folder, FlashcardDeck, Flashcard
from ..database import get_db

study_units = APIRouter()

class FlashcardRequest(BaseModel):
    deck_name: str
    user_id: str
    folder_id: Optional[str] = None
    flashcards: dict

@study_units.post("/save-study-units")
async def save_study_units(request_data: FlashcardRequest, db: Session = Depends(get_db)):
    try:
        # Convert user_id and folder_id to UUIDs
        flashcard_deck_name = request_data.deck_name
        user_id = uuid.UUID(request_data.user_id)
        folder_id = request_data.folder_id

        # Create or get folder
        folder = None
        if folder_id:
            folder = db.query(Folder).filter_by(id=uuid.UUID(folder_id)).first()

        if not folder_id or not folder:
            folder = Folder(name=flashcard_deck_name, user_id=user_id)
            db.add(folder)
            db.flush()

        # Create flashcard deck
        flashcard_deck = FlashcardDeck(
            folder_id=folder.id,
            name=flashcard_deck_name,
        )
        db.add(flashcard_deck)
        db.flush()
        flashcard_deck_id = flashcard_deck.id

        # Save flashcards
        for flashcard_type, flashcards in request_data.flashcards.items():
            cleaned_type = flashcard_type.replace("_flashcards", "")
            for flashcard in flashcards:
                flashcard_deck.flashcards.append(
                    Flashcard(
                        type=cleaned_type,
                        content=flashcard
                    )
                )
        db.commit()

        return JSONResponse(content={"flashcard_deck_id": str(flashcard_deck_id)})
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))