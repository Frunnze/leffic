import uuid
from collections.abc import Generator
from contextlib import contextmanager
from typing import cast

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app_factory import create_app
from features.account.models import ProviderKey
from shared.database import Base, get_db
from shared.models import User
from shared.password_hashing import hash_password
from tests.support import SessionProvider

PHRASE = "correct horse battery staple"
_CONFLICT = 409


def property_client() -> TestClient:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    app = create_app()
    app.dependency_overrides[get_db] = SessionProvider(
        sessionmaker(bind=engine)
    )

    return TestClient(app)


@contextmanager
def seeded_user(identifier: uuid.UUID) -> Generator[Session]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)

    with sessionmaker(bind=engine)() as session:
        session.add(
            User(
                id=identifier,
                username=f"learner-{identifier.hex}",
                email=f"{identifier.hex}@example.com",
                hashed_password=hash_password(PHRASE),
            )
        )
        session.commit()

        yield session


@contextmanager
def seeded_provider_key(
    owner: uuid.UUID, providers: list[str]
) -> Generator[Session]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)

    with sessionmaker(bind=engine)() as session:
        for provider in providers:
            session.add(
                ProviderKey(
                    user_id=owner,
                    provider=provider,
                    sealed_key="sealed",
                    salt="salt",
                    hint="tail",
                    monthly_limit_cents=None,
                    spent_cents=0,
                )
            )

        session.commit()

        yield session


def signed_up_headers(
    client: TestClient, marker: uuid.UUID, scenario: str
) -> dict[str, str]:
    credentials = fresh_credentials(marker, scenario)
    response = client.post("/sign-up", json=credentials)

    if response.status_code == _CONFLICT:
        response = client.post(
            "/login",
            json={
                "email": credentials["email"],
                "password": credentials["password"],
            },
        )

    body = cast("dict[str, str]", response.json())

    return {"Authorization": f"Bearer {body['access_token']}"}


def fresh_credentials(marker: uuid.UUID, scenario: str) -> dict[str, str]:
    tag = f"{scenario}-{marker.hex}"

    return {
        "username": f"learner-{tag}",
        "email": f"{tag}@example.com",
        "password": PHRASE,
    }
