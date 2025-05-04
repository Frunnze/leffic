from fastapi import APIRouter
from typing import List
import traceback
import tempfile
from pydantic import BaseModel
from typing import Literal, Optional
from datetime import datetime, timezone
import requests
from celery.result import AsyncResult

from ..tools.text_extractor import text_extractor_factory
from .. import ai_factory
from ..tools.prompts.flashcards_prompt import get_flashcards_system_prompt
from ..tools.prompts.notes_prompt import get_notes_system_prompt
from .. import CONTENT_MANAGEMENT_SERVICE
from .. import celery_app
from .. import ai_factory
from ..tools.prompts.flashcards_prompt import get_flashcards_system_prompt
from ..tools.prompts.notes_prompt import get_notes_system_prompt
import time


study_units_generator = APIRouter()

class FlashcardsMetadata(BaseModel):
    comprehensiveness: Optional[Literal["high", "medium", "low"]] = "medium"
    verbosity: Optional[Literal["high", "medium", "low"]] = "low"
    types: Optional[List[Literal["basic", "list", "cloze"]]] = ["basic"]
    amount: Optional[int] = None

class FileMetadata(BaseModel):
    storage_id: str
    extension: str

class StudyUnitsMetadata(BaseModel):
    user_id: str
    folder_id: Optional[str] = None
    file_metadata: List[FileMetadata]
    flashcards: Optional[FlashcardsMetadata]
    ai_model: Optional[str] = None

def get_file_from_storage(storage_name):
    with open("files/" + storage_name, "rb") as file:
        return file.read()


@celery_app.task
def generate_flashcards_task(ai_model, extracted_text, flashcards_metadata, folder_id, user_id):
    ai = ai_factory.get_ai(ai_model)

    # Sim time
    time.sleep(20)

    flashcards, _ = ai.get_ai_res(
        system_prompt=get_flashcards_system_prompt(
            comprehensiveness=flashcards_metadata['comprehensiveness'],
            verbosity=flashcards_metadata['verbosity'],
            amount=flashcards_metadata['amount'],
            flashcard_types=flashcards_metadata['types']
        ),
        user_prompt=extracted_text
    )
    deck_name = flashcards.pop("deck_name")

    # Save the flashcards in the content's db
    response = requests.post(
        url=CONTENT_MANAGEMENT_SERVICE + "/save-flashcards",
        json={
            "flashcards": flashcards,
            "deck_name": deck_name,
            "folder_id": folder_id,
            "user_id": user_id,
        }
    )
    response.raise_for_status()
    response_data = response.json()
    return {
        "flashcard_deck_id": response_data.get("flashcard_deck_id"),
        "deck_name": deck_name,
        "flashcards": flashcards,
    }


@study_units_generator.get("/flashcards-status/{task_id}")
def get_flashcard_status(task_id: str):
    task_result = AsyncResult(task_id, app=celery_app)
    if task_result.ready():
        return {
            "status": task_result.status,
            "flashcard_deck_id": task_result.result.get("flashcard_deck_id"),
            "type": "flashcard_deck",
            "name": task_result.result.get("deck_name"),
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    return {"status": task_result.status}


@study_units_generator.post("/generate-study-units")
async def generate_study_units(request_data: StudyUnitsMetadata):
    try:
        folder_id = request_data.folder_id if request_data.folder_id != "home" else request_data.user_id

        extracted_text = ""
        for file_meta in request_data.file_metadata:
            file_bytes = get_file_from_storage(file_meta.storage_id + "." + file_meta.extension)

            with tempfile.NamedTemporaryFile(suffix=file_meta.storage_id, delete=True, dir="temp_files") as temp_file:
                temp_file.write(file_bytes)
                temp_file.flush()

                text_extractor = text_extractor_factory.get_text_extractor(file_meta.extension)
                extracted_text += text_extractor.extract_text(temp_file.name, file_meta.extension) + "\n"

        # Fire off Celery tasks
        flashcard_task = generate_flashcards_task.delay(
            ai_model=request_data.ai_model,
            extracted_text=extracted_text,
            flashcards_metadata=request_data.flashcards.dict(),
            folder_id=folder_id,
            user_id=request_data.user_id
        )
        
        # Optionally trigger notes generation
        # notes_task = generate_notes_task.delay(request_data.ai_model, extracted_text)

        return {"task_id": flashcard_task.id}
    except Exception as e:
        traceback.print_exc()
        return {"err": str(e)}


@celery_app.task
def generate_notes_task(ai_model, extracted_text):
    ai = ai_factory.get_ai(ai_model)
    notes, _ = ai.get_ai_res(
        system_prompt=get_notes_system_prompt(),
        user_prompt=extracted_text
    )
    return notes