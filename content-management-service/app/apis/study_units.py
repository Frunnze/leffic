from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import uuid
import traceback
from sqlalchemy.orm import Session, aliased
from sqlalchemy import select, func, or_, exists, case
import requests
from datetime import datetime, timezone
import random

from ..models import (
    Folder, FlashcardDeck, Flashcard, 
    FlashcardReview, Note, Test, TestItem,
    TestItemReview, TestSession
)
from ..database import get_db
from .. import SCHEDULER_SERVICE
from ..tools.claims_extractor import get_user_id_from_jwt

study_units = APIRouter()


class FlashcardRequest(BaseModel):
    deck_name: str
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
    

class SaveTestRequest(BaseModel):
    test_name: str
    folder_id: Optional[str] = None
    test_items: list[dict]

@study_units.post("/save-test")
async def save_note(request_data: SaveTestRequest, db: Session = Depends(get_db)):
    try:
        new_test = Test(
            folder_id=request_data.folder_id,
            name=request_data.test_name
        )
        db.add(new_test)
        db.flush()
        new_test_id = new_test.id
        for test_item in request_data.test_items:
            new_test.test_items.append(
                TestItem(
                    content=test_item,
                    type="mult_choice",
                )
            )
        db.commit()
        return JSONResponse(content={"test_id": str(new_test_id)})
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
            "fsrs_card": flashcard.fsrs_card
        } for flashcard in flashcards
    ]

@study_units.get("/flashcards")
async def get_flashcards(
    flashcard_deck_id: Optional[str] = None, 
    folder_id: Optional[str] = None, 
    user_id: str = Depends(get_user_id_from_jwt), 
    db: Session = Depends(get_db),
    per_page: Optional[int] = 10
):
    try:
        folder_id = folder_id if folder_id != "home" else user_id

        # Get the flashcards from a specific deck
        flashcards = []
        if flashcard_deck_id:
            total_flashcards = (
                db.query(func.count(Flashcard.id))
                .filter(
                    Flashcard.deck_id == uuid.UUID(flashcard_deck_id),
                    or_(
                        func.date(Flashcard.next_review) <= datetime.now(timezone.utc).date(),
                        Flashcard.next_review.is_(None)
                    )
                )
                .scalar()
            )
            flashcards = (
                db.query(Flashcard)
                .filter(
                    Flashcard.deck_id == uuid.UUID(flashcard_deck_id),
                    or_(
                        func.date(Flashcard.next_review) <= datetime.now(timezone.utc).date(),
                        Flashcard.next_review.is_(None)
                    )
                )
                .order_by(Flashcard.next_review.asc().nullsfirst())
                .limit(per_page)
                .all()
            )
            print("(*****)", flashcard_results(flashcards))
            return JSONResponse(content={
                "flashcards": flashcard_results(flashcards),
                "total_flashcards": total_flashcards
            })

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
        total_flashcards = (
            db.query(func.count(Flashcard.id))
            .filter(
                Flashcard.deck_id.in_(deck_ids_subquery),
                or_(
                    func.date(Flashcard.next_review) <= datetime.now(timezone.utc).date(),
                    Flashcard.next_review.is_(None)
                )
            )
            .scalar()
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
            .order_by(Flashcard.next_review.asc().nullsfirst())
            .limit(per_page)
            .all()
        )
        return JSONResponse(content={
            "flashcards": flashcard_results(flashcards),
            "total_flashcards": total_flashcards
        })
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    

class ReviewFlashcardRequest(BaseModel):
    flashcard_id: int
    rating: int

@study_units.post("/review-flashcard")
async def review_flashcard(
    request_data: ReviewFlashcardRequest, 
    db: Session = Depends(get_db),
    user_id: str = Depends(get_user_id_from_jwt)
):
    try:
        # Get card
        card = db.query(Flashcard).filter_by(id=request_data.flashcard_id).first()

        # Call scheduler
        response = requests.post(
            url=SCHEDULER_SERVICE + "/schedule-flashcard",
            json={
                "card": card.fsrs_card,
                "rating": request_data.rating,
                "user_id": user_id
            }
        )
        response.raise_for_status()

        # Save new card
        response_data = response.json()
        card.fsrs_card = response_data.get("new_card")
        due_str = response_data.get("new_card").get("due")
        next_review_date = datetime.fromisoformat(due_str).replace(tzinfo=None)
        card.next_review = next_review_date

        # Add new card review log
        card.flashcard_reviews.append(
            FlashcardReview(fsrs_review=response_data.get("review_log"))
        )
        db.commit()

        return JSONResponse(content={
            "due_date": date_to_str(next_review_date),
            "new_fsrs_card": response_data.get("new_card")
        })
    except Exception as e:
        db.rollback()
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    

@study_units.get("/note")
async def get_note(note_id: str, db: Session = Depends(get_db), user_id: str = Depends(get_user_id_from_jwt)):
    try:
        note = (
            db.query(Note)
            .filter(
                Note.id == note_id
            )
            .first()
        )
        if note.read == False:
            note.read = True
            db.commit()
        return JSONResponse(content={"content": note.content, "name": note.name})
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


def get_items_test_session_answers(test_item, db, test_session):
    test_item_review = (
        db.query(TestItemReview)
        .filter(
            TestItemReview.test_session == test_session,
            TestItemReview.test_item_id == test_item.id
        )
        .first()
    )
    return test_item_review.answers if test_item_review else None

def prepare_content(content):
    new_content = {}
    new_content["question"] = content.get("question")
    options = []
    true_options = [content.get("true_option")]
    for index, option in enumerate(true_options):
        options.append({
            "id": index,
            "option": option
        })
    for index, option in enumerate(content.get("false_options")):
        options.append({
            "id": index + len(true_options),
            "option": option
        })
    random.shuffle(options)
    new_content["shuffled_options"] = options
    return new_content

@study_units.get("/test-items")
async def get_test_items(
    test_id: Optional[str] = None,
    folder_id: Optional[str] = None,
    per_page: int = 10,
    page: int = 1,
    test_session: Optional[str] = None,
    user_id: str = Depends(get_user_id_from_jwt), 
    db: Session = Depends(get_db)
):
    try:
        folder_id = folder_id if folder_id != "home" else user_id

        # Check if this origin has any unfinished test session
        if not test_session:
            test_session_obj = (
                db.query(TestSession)
                .filter(
                    TestSession.origin_id == (test_id if test_id else folder_id),
                    TestSession.status == "ongoing"
                )
                .first()
            )
            if not test_session_obj:
                new_test_session_obj = TestSession(
                    origin_id=(test_id if test_id else folder_id),
                    status="ongoing"
                )
                db.add(new_test_session_obj)
                db.flush()
                test_session = new_test_session_obj.id
                db.commit()
            else:
                test_session = test_session_obj.id

        test_items = []
        if test_id:
            total_items = (
                db.query(func.count(TestItem.id))
                .filter(TestItem.test_id == uuid.UUID(test_id))
                .scalar()
            )

            test_items = (
                db.query(TestItem)
                .filter(TestItem.test_id == uuid.UUID(test_id))
                .offset((page-1)*per_page)
                .limit(per_page)
                .all()
            )
            return JSONResponse(content={
                "test_items": [
                    {
                        "id": test_item.id,
                        "type": test_item.type,
                        "content": prepare_content(test_item.content),
                        "created_at": date_to_str(test_item.created_at),
                        "last_answers": get_items_test_session_answers(test_item, db, test_session)
                    } for test_item in test_items
                ], 
                "total_items": total_items,
                "test_session": str(test_session),
                "page": page,
                "per_page": per_page
            })

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
        test_ids_subquery = (
            select(Test.id)
            .where(Test.folder_id.in_(folder_cte))
        )
        total_items = (
            db.query(func.count(TestItem.id))
            .filter(TestItem.test_id.in_(test_ids_subquery))
            .scalar()
        )
        test_items = (
            db.query(TestItem)
            .filter(TestItem.test_id.in_(test_ids_subquery))
            .offset((page-1)*per_page)
            .limit(per_page)
            .all()
        )

        return JSONResponse(content={
            "test_items": [
                {
                    "id": test_item.id,
                    "type": test_item.type,
                    "content": prepare_content(test_item.content),
                    "created_at": date_to_str(test_item.created_at),
                    "last_answers": get_items_test_session_answers(test_item, db, test_session)
                } for test_item in test_items
            ], 
            "total_items": total_items,
            "test_session": str(test_session),
            "page": page,
            "per_page": per_page
        })
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


class ReviewTestItemRequest(BaseModel):
    test_item_id: int
    test_session: str
    answers: list

def evaluate_accuracy(user_answers, db):
    if user_answers[0] == 0:
        return 1
    return 0

@study_units.post("/review-test-item")
async def review_test_item(
    req_data: ReviewTestItemRequest,
    db: Session = Depends(get_db)
):
    try:
        test_item = db.query(TestItem).filter_by(id=req_data.test_item_id).first()
        test_item_review = (
            db.query(TestItemReview)
            .filter(
                TestItemReview.test_item_id == req_data.test_item_id,
                TestItemReview.test_session == req_data.test_session
            )
            .first()
        )
        if not test_item_review:
            db.add(TestItemReview(
                test_session=uuid.UUID(req_data.test_session),
                test_item_id=req_data.test_item_id,
                accuracy=evaluate_accuracy(req_data.answers, db),
                answers=req_data.answers,
                reviewed_at=datetime.now(timezone.utc)
            ))
        else:
            test_item_review.answers = req_data.answers
            test_item_review.reviewed_at = datetime.now(timezone.utc)
            test_item_review.accuracy = evaluate_accuracy(req_data.answers, db)

        db.commit()
        return JSONResponse(content={"msg": "Saved!"})
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    

@study_units.get("/test-items-stats")
async def test_items_stats(
    folder_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_user_id_from_jwt)
):
    try:
        folder_id = folder_id if folder_id != "home" else user_id
        
        # Recursive CTE to get all subfolder IDs
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
            select(subfolder.id)
            .where(subfolder.parent_id == folder_cte.c.id)
        )
        
        total_items = (
            db.query(func.count(TestItem.id))
            .join(Test, Test.id == TestItem.test_id)
            .filter(Test.folder_id.in_(folder_cte))
            .scalar()
        )

        avg_accuracy_subquery = (
            db.query(
                TestItemReview.test_item_id.label("test_item_id"),
                func.avg(TestItemReview.accuracy).label("avg_accuracy")
            )
            .join(TestItem, TestItem.id == TestItemReview.test_item_id)
            .join(Test, Test.id == TestItem.test_id)
            .filter(TestItemReview.accuracy != None)
            .filter(Test.folder_id.in_(folder_cte))
            .group_by(TestItemReview.test_item_id)
            .subquery()
        )
        correct_items = (
            db.query(func.count())
            .select_from(avg_accuracy_subquery)
            .filter(avg_accuracy_subquery.c.avg_accuracy >= 0.9)
            .scalar()
        )
        if total_items > 0:
            return JSONResponse(content={
                "total": total_items,
                "correct": correct_items if correct_items else 0
            })
        return JSONResponse(content={"msg": "No test stats!"}, status_code=404)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@study_units.get("/test-session-results")
async def test_session_results(
    test_session: str,
    db: Session = Depends(get_db)
):
    try:
        result = (
            db.query(
                func.sum(
                    case(
                        (TestItemReview.accuracy == 1.0, 1),
                        else_=0
                    )
                ).label('correct')
            )
            .filter(
                TestItemReview.accuracy != None,
                TestItemReview.test_session == test_session
            )
            .one()
        )

        # End the test session
        test_session = db.query(TestSession).filter_by(id=test_session).first()
        test_session.status = "done"
        db.commit()
        
        if result.correct:
            return JSONResponse(content={"correct": result.correct})
        return JSONResponse(content={"msg": "No test stats!"}, status_code=404)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@study_units.get("/flashcards-stats")
async def get_flashcards_stats(
    folder_id: Optional[str] = None, 
    user_id: str = Depends(get_user_id_from_jwt), 
    db: Session = Depends(get_db)
):
    try:
        folder_id = folder_id if folder_id != "home" else user_id

        user_folder_exists = db.query(
            exists().where(Folder.user_id == user_id, Folder.id == folder_id)
        ).scalar()
        if not user_folder_exists:
            raise HTTPException(status_code=404, detail="Folder does not exist!")

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

        due_flashcards = (
            db.query(func.count(Flashcard.id))
            .filter(
                Flashcard.deck_id.in_(deck_ids_subquery),
                or_(
                    func.date(Flashcard.next_review) <= datetime.now(timezone.utc).date(),
                    Flashcard.next_review == None
                )
            )
            .scalar()
        )

        done_flashcards = (
            db.query(func.count(Flashcard.id))
            .filter(
                Flashcard.deck_id.in_(deck_ids_subquery),
                func.date(Flashcard.next_review) > datetime.now(timezone.utc).date(),
                Flashcard.next_review != None
            )
            .scalar()
        )

        if due_flashcards == 0 and done_flashcards == 0:
            return JSONResponse(content={"msg": "No flashcards!"}, status_code=404)

        return JSONResponse(content={
            "due": due_flashcards,
            "done": done_flashcards
        })
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    

@study_units.get("/notes-stats")
async def get_notes_stats(
    folder_id: Optional[str] = None, 
    user_id: str = Depends(get_user_id_from_jwt), 
    db: Session = Depends(get_db)
):
    try:
        folder_id = folder_id if folder_id != "home" else user_id

        user_folder_exists = db.query(
            exists().where(Folder.user_id == user_id, Folder.id == folder_id)
        ).scalar()
        if not user_folder_exists:
            raise HTTPException(status_code=404, detail="Folder does not exist!")

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

        due_notes = (
            db.query(func.count(Note.id))
            .filter(
                Note.folder_id.in_(folder_cte),
                Note.read == False
            )
            .scalar()
        )

        read_notes = (
            db.query(func.count(Note.id))
            .filter(
                Note.folder_id.in_(folder_cte),
                Note.read == True
            )
            .scalar()
        )
     
        if read_notes == 0 and due_notes == 0:
            return JSONResponse(content={"msg": "No notes!"}, status_code=404)
        
        return JSONResponse(content={
            "due": due_notes,
            "read": read_notes
        })
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))