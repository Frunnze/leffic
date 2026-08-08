from fastapi import FastAPI


def create_app():
    app = FastAPI()

    from src.features.flashcard_scheduling.flashcard_scheduler_router import (
        flashcard_scheduler
    )
    app.include_router(flashcard_scheduler)

    return app
