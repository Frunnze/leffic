from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.features.file_system.content_router import content_router
from src.features.file_system.folder_router import folder_router
from src.features.study_units.assessment_router import assessment_router
from src.features.study_units.flashcard_router import flashcard_router
from src.features.study_units.note_router import note_router
from src.features.study_units.study_unit_saving import study_unit_saving
from src.shared.database import Base, engine


def create_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(study_unit_saving)
    app.include_router(flashcard_router)
    app.include_router(assessment_router)
    app.include_router(note_router)
    app.include_router(folder_router)
    app.include_router(content_router)

    Base.metadata.create_all(bind=engine)

    return app
