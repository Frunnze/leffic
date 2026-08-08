from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from features.chatbot.chatbot import chatbot
from features.file_upload.file_uploader import file_uploader
from features.study_units_generation.study_units_router import (
    study_units_router,
)
from features.study_units_generation.task_status_router import (
    task_status_router,
)


def create_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(study_units_router)
    app.include_router(task_status_router)
    app.include_router(file_uploader)
    app.include_router(chatbot)

    return app
