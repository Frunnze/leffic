from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware


load_dotenv()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_app():
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
    )

    from .apis.auth import auth
    app.include_router(auth)

    from . import models
    from .database import engine
    models.Base.metadata.create_all(bind=engine)

    return app