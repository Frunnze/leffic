from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import uuid
import traceback
from sqlalchemy.orm import Session
import requests
from datetime import datetime

from ..models import Folder, FlashcardDeck, Flashcard, FlashcardReview
from ..database import get_db
from .. import SCHEDULER_SERVICE

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
    

def str_date(dateobj):
    return dateobj.strftime("%Y-%m-%d %H:%M:%S")

def get_deck_flashcards(db, flashcard_deck_id):
    flashcards = (
        db.query(Flashcard)
        .filter(
            Flashcard.deck_id == uuid.UUID(flashcard_deck_id)
        )
        .all()
    )
    return [
        {
            "id": flashcard.id,
            "type": flashcard.type,
            "next_review": flashcard.next_review,
            "content": flashcard.content,
            "created_at": str_date(flashcard.created_at),
            "future_ratings_time": flashcard.future_ratings_time if flashcard.future_ratings_time else {1: 59, 2: 329, 3: 599, 4: 86399}
        } for flashcard in flashcards
    ]

@study_units.get("/flashcards")
async def get_flashcards(flashcard_deck_id: Optional[str] = None, folder_id: Optional[str] = None, db: Session = Depends(get_db)):
    try:
        flashcards = []
        if flashcard_deck_id:
            flashcards = get_deck_flashcards(db, flashcard_deck_id)
            return JSONResponse(content={"flashcards": flashcards})

        return JSONResponse(content={"flashcards": flashcards})
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    

class ReviewFlashcardRequest(BaseModel):
    flashcard_id: int
    rating: int
    user_id: str

@study_units.post("/review-flashcard")
async def review_flashcard(request_data: ReviewFlashcardRequest, db: Session = Depends(get_db)):
    try:
        # Get card
        card = db.query(Flashcard).filter_by(id=request_data.flashcard_id).first()

        # Call scheduler
        response = requests.post(
            url=SCHEDULER_SERVICE + "/schedule-flashcard",
            json={
                "card": card.fsrs_card,
                "rating": request_data.rating,
                "user_id": request_data.user_id
            }
        )
        response.raise_for_status()

        # Save new card
        response_data = response.json()
        card.fsrs_card = response_data.get("new_card")
        due_str = response_data.get("new_card").get("due")
        card.next_review = datetime.fromisoformat(due_str)
        card.future_ratings_time = response_data.get("ratings_time")

        # Add new card review log
        card.flashcard_reviews.append(
            FlashcardReview(fsrs_review=response_data.get("review_log"))
        )

        db.commit()
        return JSONResponse(content={
            "due_date": response_data.get("new_card").get("due"), 
            "future_ratings_time": response_data.get("ratings_time")}
        )
    except Exception as e:
        db.rollback()
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))