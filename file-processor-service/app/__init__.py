from fastapi import FastAPI
from dotenv import load_dotenv
import os
from fastapi.middleware.cors import CORSMiddleware
from celery import Celery


from .tools.ai_manager import AIFactory

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST")
CONTENT_MANAGEMENT_SERVICE = os.getenv("CONTENT_MANAGEMENT_SERVICE")
ai_factory = AIFactory()
celery_app = Celery(
    'app',
    broker=f'redis://{REDIS_HOST}',
    backend=f'redis://{REDIS_HOST}',
    include=["app.apis.study_units_generator"]
)


def create_app():
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    from .apis.study_units_generator import study_units_generator
    from .apis.file_uploader import file_uploader
    app.include_router(study_units_generator)
    app.include_router(file_uploader)
   

    return app