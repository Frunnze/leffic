from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app_factory import create_app
from features.authentication import cookie_security
from shared.database import Base, get_db
from tests.support import Accounts, SessionProvider


@pytest.fixture
def client() -> Iterator[TestClient]:
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

    with TestClient(app) as test_client:
        yield test_client

    Base.metadata.drop_all(bind=engine)


def test_the_sign_up_refresh_cookie_is_secure(client: TestClient) -> None:
    response = client.post(
        "/sign-up",
        json={
            "username": Accounts.username,
            "email": Accounts.email,
            "password": Accounts.phrase,
        },
    )

    assert "Secure" in response.headers["set-cookie"]


def test_the_login_refresh_cookie_is_secure(client: TestClient) -> None:
    _ = Accounts(client).sign_up()

    response = client.post(
        "/login",
        json={"email": Accounts.email, "password": Accounts.phrase},
    )

    assert "Secure" in response.headers["set-cookie"]


def test_the_logout_cookie_removal_is_secure(client: TestClient) -> None:
    _ = Accounts(client).sign_up()

    response = client.post("/logout")

    assert "Secure" in response.headers["set-cookie"]


def test_a_plain_http_deployment_can_drop_the_secure_flag(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(cookie_security, "REFRESH_COOKIE_SECURE", False)

    response = client.post(
        "/sign-up",
        json={
            "username": Accounts.username,
            "email": Accounts.email,
            "password": Accounts.phrase,
        },
    )

    assert "Secure" not in response.headers["set-cookie"]
