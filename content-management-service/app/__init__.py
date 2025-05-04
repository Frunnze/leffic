from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os


SCHEDULER_SERVICE = os.getenv("SCHEDULER_SERVICE")

def create_app():
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    from .apis.study_units import study_units
    app.include_router(study_units)

    from .apis.file_system_manager import file_system_manager
    app.include_router(file_system_manager)

    from . import models
    from .database import engine
    models.Base.metadata.create_all(bind=engine)

    return app