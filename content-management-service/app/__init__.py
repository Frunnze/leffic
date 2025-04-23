from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = FastAPI()

    from .apis.study_units import study_units
    app.include_router(study_units)

    from .apis.file_system_manager import file_system_manager
    app.include_router(file_system_manager)

    from . import models
    from .database import engine
    models.Base.metadata.create_all(bind=engine)

    return app