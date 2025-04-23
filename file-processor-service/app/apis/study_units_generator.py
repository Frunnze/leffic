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

study_units_generator = APIRouter()
CONTENT_MANAGEMENT_SERVICE = os.getenv("CONTENT_MANAGEMENT_SERVICE")

class FlashcardsMetadata(BaseModel):
    comprehensiveness: Literal["high", "medium", "low"] = "medium"
    verbosity: Literal["high", "medium", "low"] = "low"
    types: List[Literal["basic", "list", "cloze"]] = ["basic"]
    amount: Optional[int] = None

class StudyUnitsMetadata(BaseModel):
    user_id: str
    folder_id: Optional[str] = None
    files_ids: List[str]
    flashcards: FlashcardsMetadata
    ai_model: Optional[str] = None

def get_file_from_storage(file_id):
    with open("files/" + file_id, "rb") as file:
        return file.read()

@study_units_generator.post("/generate-study-units/")
async def generate_study_units(metadata: StudyUnitsMetadata):
    try:
        # Check if the user has enough resources
        # ... (request to user service)

        # Extract the text
        extracted_text = ""
        for file_id in metadata.files_ids:
            file_bytes = get_file_from_storage(file_id)

            with tempfile.NamedTemporaryFile(suffix=file_id, delete=True, dir="temp_files") as temp_file:
                temp_file.write(file_bytes)
                temp_file.flush() 

                _, extension = os.path.splitext(file_id)
                extension = extension.lstrip(".")

                text_extractor = text_extractor_factory\
                    .get_text_extractor(extension)
                extracted_text += text_extractor.extract_text(temp_file.name, extension) + "\n"

        # Check if the current resources are enough for the extracted text 
        # ...

        # Generate study units
        ai = ai_factory.get_ai(metadata.ai_model)
        flashcards, request_cost = ai.get_ai_res(
            system_prompt=get_flashcards_system_prompt(
                comprehensiveness=metadata.flashcards.comprehensiveness,
                verbosity=metadata.flashcards.verbosity,
                amount=metadata.flashcards.amount,
                flashcard_types=metadata.flashcards.types
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
            "folder_id": metadata.folder_id, 
            "user_id": metadata.user_id
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