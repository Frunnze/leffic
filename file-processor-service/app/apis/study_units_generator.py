from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
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
from ..tools.prompts.tests_prompt import get_test_system_prompt
from ..tools.claims_extractor import get_user_id_from_jwt
from ..tools.link_extractor import extract_link_main_content, get_youtube_transcript_auto


study_units_generator = APIRouter()


def get_file_from_storage(storage_name):
    with open("files/" + storage_name, "rb") as file:
        return file.read()


@celery_app.task
def generate_flashcards_task(ai_model, extracted_text, flashcards_metadata, folder_id, user_id):
    ai = ai_factory.get_ai(ai_model)

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
        "deck_name": deck_name
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


@celery_app.task
def generate_note_task(ai_model, extracted_text, folder_id, user_id):
    ai = ai_factory.get_ai(ai_model)
    note, _ = ai.get_ai_res(
        system_prompt=get_notes_system_prompt(),
        user_prompt=extracted_text
    )
    
    # Save the flashcards in the content's db
    response = requests.post(
        url=CONTENT_MANAGEMENT_SERVICE + "/save-note",
        json={
            "note_content": note.get("note_content"),
            "note_name": note.get("note_name"),
            "folder_id": folder_id,
            "user_id": user_id,
        }
    )
    response.raise_for_status()
    response_data = response.json()
    return {
        "note_id": response_data.get("note_id"),
        "note_name": note.get("note_name"),
    }


@celery_app.task
def generate_test_task(ai_model, extracted_text, folder_id, user_id):
    ai = ai_factory.get_ai(ai_model)
    test, _ = ai.get_ai_res(
        system_prompt=get_test_system_prompt(),
        user_prompt=extracted_text
    )

    response = requests.post(
        url=CONTENT_MANAGEMENT_SERVICE + "/save-test",
        json={
            "test_items": test.get("multiple_choice_test_items"),
            "test_name": test.get("test_name"),
            "folder_id": folder_id,
            "user_id": user_id,
        }
    )
    response.raise_for_status()
    response_data = response.json()
    return {
        "test_id": response_data.get("test_id"),
        "test_name": test.get("test_name"),
    }


@study_units_generator.get("/test-task-status/{task_id}")
def get_test_task_status(task_id: str):
    task_result = AsyncResult(task_id, app=celery_app)
    if task_result.ready():
        return {
            "status": task_result.status,
            "test_id": task_result.result.get("test_id"),
            "type": "test",
            "name": task_result.result.get("test_name"),
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    return {"status": task_result.status}


@study_units_generator.get("/note-task-status/{task_id}")
def get_note_task_status(task_id: str):
    task_result = AsyncResult(task_id, app=celery_app)
    if task_result.ready():
        return {
            "status": task_result.status,
            "note_id": task_result.result.get("note_id"),
            "type": "note",
            "name": task_result.result.get("note_name"),
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    return {"status": task_result.status}

class FlashcardsMetadata(BaseModel):
    comprehensiveness: Optional[Literal["high", "medium", "low"]] = "medium"
    verbosity: Optional[Literal["high", "medium", "low"]] = "low"
    types: Optional[List[Literal["basic", "list", "cloze"]]] = ["basic"]
    amount: Optional[int] = None

class FileMetadata(BaseModel):
    file_id: str
    extension: str

class NoteMetadata(BaseModel):
    pass

class TestMetadata(BaseModel):
    amount: int = 10

class StudyUnitsMetadata(BaseModel):
    folder_id: Optional[str] = None
    file_metadata: Optional[List[FileMetadata]] = None
    link_metadata: Optional[str] = None
    topic_metadata: Optional[str] = None
    flashcards: Optional[FlashcardsMetadata] = None
    note: Optional[NoteMetadata] = None
    test: Optional[TestMetadata] = None
    ai_model: Optional[str] = None

@study_units_generator.post("/generate-study-units")
async def generate_study_units(
    request_data: StudyUnitsMetadata, 
    user_id: str = Depends(get_user_id_from_jwt)
):
    try:
        folder_id = request_data.folder_id if request_data.folder_id != "home" else user_id

        extracted_text = ""
        if request_data.file_metadata:
            for file_meta in request_data.file_metadata:
                file_bytes = get_file_from_storage(file_meta.file_id + "." + file_meta.extension)

                with tempfile.NamedTemporaryFile(suffix=file_meta.file_id, delete=True, dir="temp_files") as temp_file:
                    temp_file.write(file_bytes)
                    temp_file.flush()

                    text_extractor = text_extractor_factory.get_text_extractor(file_meta.extension)
                    extracted_text += text_extractor.extract_text(temp_file.name, file_meta.extension) + "\n"
        elif request_data.link_metadata:
            if "youtube.com" in request_data.link_metadata:
                extracted_text = get_youtube_transcript_auto(request_data.link_metadata)
            if not extracted_text:
                extracted_text = extract_link_main_content(request_data.link_metadata)
        elif request_data.topic_metadata:
            extracted_text += f"Topic: {request_data.topic_metadata}"

        if not extracted_text:
            return JSONResponse(
                content={"msg": "Could not extract text!"},
                status_code=400
            )
        if request_data.link_metadata:
            extracted_text += f"The source link to mention in notes: {request_data.link_metadata}"

        response_data = {}        
        if request_data.note:
            note_task = generate_note_task.delay(
                ai_model=request_data.ai_model, 
                extracted_text=extracted_text,
                folder_id=folder_id,
                user_id=user_id
            )
            response_data["note_task_id"] = note_task.id

        if request_data.flashcards:
            flashcard_task = generate_flashcards_task.delay(
                ai_model=request_data.ai_model,
                extracted_text=extracted_text,
                flashcards_metadata=request_data.flashcards.dict(),
                folder_id=folder_id,
                user_id=user_id
            )
            response_data["task_id"] = flashcard_task.id

        if request_data.test:
            test_task = generate_test_task.delay(
                ai_model=request_data.ai_model, 
                extracted_text=extracted_text,
                folder_id=folder_id,
                user_id=user_id
            )
            response_data["test_task_id"] = test_task.id

        return response_data
    except Exception as e:
        traceback.print_exc()
        return {"err": str(e)}