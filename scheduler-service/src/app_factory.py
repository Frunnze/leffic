from fastapi import FastAPI

from src.features.flashcard_scheduling.flashcard_scheduler_router import (
    flashcard_scheduler,
)


def create_app() -> FastAPI:
    app = FastAPI()
    app.include_router(flashcard_scheduler)

    return app
