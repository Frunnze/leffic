from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def create_app():
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    from src.features.study_units_generation.study_units_generator import (
        study_units_generator
    )
    from src.features.file_upload.file_uploader import file_uploader
    from src.features.chatbot.chatbot import chatbot
    app.include_router(study_units_generator)
    app.include_router(file_uploader)
    app.include_router(chatbot)

    return app
