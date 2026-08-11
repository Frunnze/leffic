from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from features.chatbot.chatbot import chatbot
from features.file_system.content_router import content_router
from features.file_system.folder_router import folder_router
from features.file_system.unit_router import unit_router
from features.file_upload.file_uploader import file_uploader
from features.scheduling.rating_intervals_router import (
    rating_intervals_router,
)
from features.study_units.assessment_editing_router import (
    assessment_editing_router,
)
from features.study_units.assessment_router import assessment_router
from features.study_units.assessment_stats_router import (
    assessment_stats_router,
)
from features.study_units.flashcard_editing_router import (
    flashcard_editing_router,
)
from features.study_units.flashcard_router import flashcard_router
from features.study_units.flashcard_stats_router import (
    flashcard_stats_router,
)
from features.study_units.note_router import note_router
from features.study_units_generation.extraction_router import (
    extraction_router,
)
from features.study_units_generation.generation_router import (
    generation_router,
)
from features.study_units_generation.task_status_router import (
    task_status_router,
)
from shared.database import Base, engine


def create_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(flashcard_router)
    app.include_router(flashcard_editing_router)
    app.include_router(flashcard_stats_router)
    app.include_router(assessment_router)
    app.include_router(assessment_editing_router)
    app.include_router(assessment_stats_router)
    app.include_router(note_router)
    app.include_router(folder_router)
    app.include_router(content_router)
    app.include_router(unit_router)
    app.include_router(chatbot)
    app.include_router(file_uploader)
    app.include_router(rating_intervals_router)
    app.include_router(extraction_router)
    app.include_router(generation_router)
    app.include_router(task_status_router)

    Base.metadata.create_all(bind=engine)

    return app
