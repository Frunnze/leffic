from fastapi import APIRouter
from typing import List
import traceback
import tempfile
from pydantic import BaseModel
from typing import Literal, Optional
import os
import requests

from ..tools.text_extractor import text_extractor_factory
from .. import ai_factory
from ..tools.prompts.flashcards_prompt import get_flashcards_system_prompt
from .. import CONTENT_MANAGEMENT_SERVICE

study_units_generator = APIRouter()

class FlashcardsMetadata(BaseModel):
    comprehensiveness: Literal["high", "medium", "low"] = "medium"
    verbosity: Literal["high", "medium", "low"] = "low"
    types: List[Literal["basic", "list", "cloze"]] = ["basic"]
    amount: Optional[int] = None

class FileMetadata(BaseModel):
    storage_id: str
    extension: str

class StudyUnitsMetadata(BaseModel):
    user_id: str
    folder_id: Optional[str] = None
    file_metadata: List[FileMetadata]
    flashcards: FlashcardsMetadata
    ai_model: Optional[str] = None

def get_file_from_storage(storage_name):
    with open("files/" + storage_name, "rb") as file:
        return file.read()

@study_units_generator.post("/generate-study-units/")
async def generate_study_units(request_data: StudyUnitsMetadata):
    try:
        # Check if the user has enough resources
        # ... (request to user service)

        # Extract the text
        extracted_text = ""
        for file_meta in request_data.file_metadata:
            file_bytes = get_file_from_storage(file_meta.storage_id + "." + file_meta.extension)

            with tempfile.NamedTemporaryFile(suffix=file_meta.storage_id, delete=True, dir="temp_files") as temp_file:
                temp_file.write(file_bytes)
                temp_file.flush()

                text_extractor = text_extractor_factory\
                    .get_text_extractor(file_meta.extension)
                extracted_text += text_extractor.extract_text(temp_file.name, file_meta.extension) + "\n"

        # Check if the current resources are enough for the extracted text 
        # ...

        # Generate study units
        ai = ai_factory.get_ai(request_data.ai_model)
        flashcards, request_cost = ai.get_ai_res(
            system_prompt=get_flashcards_system_prompt(
                comprehensiveness=request_data.flashcards.comprehensiveness,
                verbosity=request_data.flashcards.verbosity,
                amount=request_data.flashcards.amount,
                flashcard_types=request_data.flashcards.types
            ),
            user_prompt=extracted_text
        )
        deck_name = flashcards.pop("deck_name")
        
        # Substract the request cost
        #...

        # Save study units
        data = {
            "flashcards": flashcards,
            "deck_name": deck_name,
            "folder_id": request_data.folder_id, 
            "user_id": request_data.user_id
        }
        response = requests.post(
            url=CONTENT_MANAGEMENT_SERVICE + "/save-study-units",
            json=data
        )
        response.raise_for_status()
        response_data = response.json()

        # Return study units to the front (?)
        return {
            "flashcard_deck_id": response_data.get("flashcard_deck_id"),
            # "flashcards": flashcards,
            # "request_cost": request_cost
        }
    except Exception as e:
        traceback.print_exc()
        return {"err": str(e)}