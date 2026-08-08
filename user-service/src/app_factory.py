from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware


load_dotenv()

def create_app():
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    from src.features.authentication.authentication_router import auth
    app.include_router(auth)

    from src.features.authentication import models
    from src.shared.database import engine
    models.Base.metadata.create_all(bind=engine)

    return app