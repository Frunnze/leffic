from collections.abc import Iterator
from typing import cast

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app_factory import create_app
from shared.database import Base, get_db

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


def test_sign_up_returns_the_new_user_and_a_token(
    client: TestClient,
) -> None:
    body = _sign_up(client)

    assert body["email"] == _EMAIL
    assert body["access_token"]


def test_sign_up_sets_a_refresh_cookie(client: TestClient) -> None:
    _ = _sign_up(client)

    assert "refresh_token" in client.cookies


def test_sign_up_rejects_a_duplicate_username(client: TestClient) -> None:
    _ = _sign_up(client)

    response = client.post(
        "/sign-up",
        json={
            "username": _USERNAME,
            "email": "other@example.com",
            "password": _LOGIN_PHRASE,
        },
    )

    assert response.status_code == 409
    assert response.json() == "Username already registered"


def test_sign_up_rejects_a_duplicate_email(client: TestClient) -> None:
    _ = _sign_up(client)

    response = client.post(
        "/sign-up",
        json={
            "username": "someone-else",
            "email": _EMAIL,
            "password": _LOGIN_PHRASE,
        },
    )

    assert response.status_code == 409
    assert response.json() == "Email already registered"


def test_login_returns_a_token_for_the_right_password(
    client: TestClient,
) -> None:
    _ = _sign_up(client)

    response = client.post(
        "/login", json={"email": _EMAIL, "password": _LOGIN_PHRASE}
    )

    assert response.status_code == 200
    assert response.json()["username"] == _USERNAME


def test_login_rejects_an_unknown_email(client: TestClient) -> None:
    response = client.post(
        "/login",
        json={"email": "nobody@example.com", "password": _LOGIN_PHRASE},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Incorrect email"


def test_login_rejects_a_wrong_password(client: TestClient) -> None:
    _ = _sign_up(client)

    response = client.post(
        "/login", json={"email": _EMAIL, "password": "not-the-password"}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Incorrect password"
