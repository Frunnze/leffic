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

    from src.features.study_units.study_units_router import study_units
    app.include_router(study_units)

    from src.features.file_system.file_system_router import file_system_manager
    app.include_router(file_system_manager)

    from src.shared import models
    from src.shared.database import engine
    models.Base.metadata.create_all(bind=engine)

    return app
