from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from features.account.account_router import account_router
from features.account.provider_key_router import provider_key_router
from features.account.theme_router import theme_router
from features.authentication.authentication_router import auth
from shared.database import Base, engine

_ = load_dotenv()

_ALLOWED_ORIGIN = "http://localhost:3009"


def create_app() -> FastAPI:
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[_ALLOWED_ORIGIN],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth)
    app.include_router(account_router)
    app.include_router(provider_key_router)
    app.include_router(theme_router)

    Base.metadata.create_all(bind=engine)

    return app
