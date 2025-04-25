from fastapi import FastAPI
from pymongo import MongoClient
import os


client = MongoClient(f"mongodb://{os.getenv('MONGODB_HOST')}")
db = client["fsrs_db"]

def create_app():
    app = FastAPI()

    from .apis.flashcard_scheduler import flashcard_scheduler
    app.include_router(flashcard_scheduler)

    return app