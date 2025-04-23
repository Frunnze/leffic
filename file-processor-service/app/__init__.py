from fastapi import FastAPI
from dotenv import load_dotenv
import os

from .tools.ai_manager import AIFactory

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST")
ai_factory = AIFactory()

def create_app():
    app = FastAPI()

    from .apis.study_units_generator import study_units_generator
    from .apis.file_uploader import file_uploader
    app.include_router(study_units_generator)
    app.include_router(file_uploader)

    from . import models
    from .database import engine
    models.Base.metadata.create_all(bind=engine)

    return app