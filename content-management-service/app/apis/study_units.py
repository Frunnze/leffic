from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List
import uuid
import traceback
from sqlalchemy.orm import Session, aliased
from sqlalchemy import select, func, or_
import requests
from datetime import datetime, timezone

from ..models import Folder, FlashcardDeck, Flashcard, FlashcardReview, Note
from ..database import get_db
from .. import SCHEDULER_SERVICE

study_units = APIRouter()


class FlashcardRequest(BaseModel):
    deck_name: str
    user_id: str
    folder_id: Optional[str] = None
    flashcards: dict

@study_units.post("/save-flashcards")
async def save_flashcards(request_data: FlashcardRequest, db: Session = Depends(get_db)):
    try:
        # Convert user_id and folder_id to UUIDs
        flashcard_deck_name = request_data.deck_name

        # Create or get folder
        folder = db.query(Folder).filter_by(id=request_data.folder_id).first()

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
    

class SaveNoteRequest(BaseModel):
    note_content: str
    note_name: str
    folder_id: Optional[str] = None
    user_id: str

@study_units.post("/save-note")
async def save_note(request_data: SaveNoteRequest, db: Session = Depends(get_db)):
    try:
        new_note = Note(
            folder_id=request_data.folder_id,
            name=request_data.note_name,
            content=request_data.note_content,
            type="general"
        )
        db.add(new_note)
        db.flush()
        new_note_id = new_note.id
        db.commit()
        return JSONResponse(content={"note_id": str(new_note_id)})
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    

def date_to_str(dateobj):
    return dateobj.strftime("%Y-%m-%d %H:%M:%S")

def flashcard_results(flashcards):
    return [
        {
            "id": flashcard.id,
            "type": flashcard.type,
            "next_review": date_to_str(flashcard.next_review) if flashcard.next_review else None,
            "content": flashcard.content,
            "created_at": date_to_str(flashcard.created_at),
            "future_ratings_time": flashcard.future_ratings_time if flashcard.future_ratings_time else {1: 59, 2: 329, 3: 599, 4: 86399}
        } for flashcard in flashcards
    ]

@study_units.get("/flashcards")
async def get_flashcards(user_id: str, flashcard_deck_id: Optional[str] = None, folder_id: Optional[str] = None, db: Session = Depends(get_db)):
    try:
        folder_id = folder_id if folder_id != "home" else user_id
        # Trigger the optimizer from the scheduler service
        # ...

        # Get the flashcards from a specific deck
        flashcards = []
        if flashcard_deck_id:
            flashcards = (
                db.query(Flashcard)
                .filter(
                    Flashcard.deck_id == uuid.UUID(flashcard_deck_id),
                    or_(
                        func.date(Flashcard.next_review) <= datetime.now(timezone.utc).date(),
                        Flashcard.next_review.is_(None)
                    )
                )
                .order_by(Flashcard.next_review.asc())
                .all()
            )
            return JSONResponse(content={"flashcards": flashcard_results(flashcards)})

        # Get the flashcards from a folder and its subfolders
        folder_cte = (
            select(Folder.id)
            .where(
                Folder.id == folder_id,
                Folder.user_id == user_id
            )
            .cte(name="subfolders", recursive=True)
        )
        subfolder = aliased(Folder)
        folder_cte = folder_cte.union_all(
            select(subfolder.id).where(subfolder.parent_id == folder_cte.c.id)
        )
        deck_ids_subquery = (
            select(FlashcardDeck.id)
            .where(FlashcardDeck.folder_id.in_(folder_cte))
        )
        flashcards = (
            db.query(Flashcard)
            .filter(
                Flashcard.deck_id.in_(deck_ids_subquery),
                or_(
                    func.date(Flashcard.next_review) <= datetime.now(timezone.utc).date(),
                    Flashcard.next_review.is_(None)
                )
            )
            .order_by(Flashcard.next_review.asc())
            .all()
        )

        return JSONResponse(content={"flashcards": flashcard_results(flashcards)})
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
    

@study_units.get("/note")
async def get_note(note_id: str, db: Session = Depends(get_db)):
    try:
        result = (
            db.query(Note)
            .filter(Note.id == note_id)
            .first()
        )
        return JSONResponse(content={"content": result.content, "name": result.name})
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))