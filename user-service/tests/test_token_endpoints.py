from collections.abc import Iterator
from typing import cast

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app_factory import create_app
from features.authentication.access import (
    ALGORITHM,
    SECRET_KEY,
    create_refresh_token,
)
from shared.database import Base, get_db

_OK = 200
_UNAUTHORIZED = 401

_EMAIL = "learner@example.com"
_USERNAME = "learner"
_LOGIN_PHRASE = "correct horse battery staple"


class SessionProvider:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        super().__init__()
        self.session_factory: sessionmaker[Session] = session_factory

    def __call__(self) -> Iterator[Session]:
        session = self.session_factory()
        try:
            yield session
        finally:
            session.close()


@pytest.fixture
def client() -> Iterator[TestClient]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine)
    app = create_app()
    app.dependency_overrides[get_db] = SessionProvider(session_factory)

    with TestClient(app) as test_client:
        yield test_client

    Base.metadata.drop_all(bind=engine)


def _sign_up(client: TestClient, email: str = _EMAIL) -> dict[str, object]:
    response = client.post(
        "/sign-up",
        json={
            "username": _USERNAME,
            "email": email,
            "password": _LOGIN_PHRASE,
        },
    )

    return cast("dict[str, object]", response.json())


def test_refresh_token_issues_a_new_access_token(
    client: TestClient,
) -> None:
    body = _sign_up(client)
    user_id = str(body["user_id"])

    response = client.post("/refresh-token")

    assert response.status_code == _OK
    assert response.json()["user_id"] == user_id


def test_refresh_token_rejects_a_missing_cookie(client: TestClient) -> None:
    response = client.post("/refresh-token")

    assert response.status_code == _UNAUTHORIZED
    assert response.json()["detail"] == "Missing refresh token"


def test_refresh_token_rejects_a_forged_cookie(client: TestClient) -> None:
    client.cookies.set("refresh_token", "not-a-jwt")

    response = client.post("/refresh-token")

    assert response.status_code == _UNAUTHORIZED
    assert response.json()["detail"] == "Invalid token"


def test_refresh_token_rejects_a_token_without_a_user_id(
    client: TestClient,
) -> None:
    token = jwt.encode({"iss": "my-issuer"}, SECRET_KEY, algorithm=ALGORITHM)
    client.cookies.set("refresh_token", token)

    response = client.post("/refresh-token")

    assert response.status_code == _UNAUTHORIZED
    assert response.json()["detail"] == "Invalid token"


def test_refresh_token_accepts_a_valid_refresh_token(
    client: TestClient,
) -> None:
    user_id = "6f1c7d4e-0000-4000-8000-000000000001"
    client.cookies.set(
        "refresh_token", create_refresh_token({"user_id": user_id})
    )

    response = client.post("/refresh-token")

    assert response.json()["user_id"] == user_id


def test_logout_clears_the_refresh_cookie(client: TestClient) -> None:
    _ = _sign_up(client)

    response = client.post("/logout")

    assert response.status_code == _OK
    assert response.json()["message"] == "Successfully logged out"
