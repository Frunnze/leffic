from collections.abc import Iterator
from typing import cast

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app_factory import create_app
from shared.database import Base, get_db
from tests.support import Accounts, SessionProvider

_OK = 200
_UNAUTHORIZED = 401
_UNPROCESSABLE_ENTITY = 422


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


@pytest.fixture
def accounts(client: TestClient) -> Accounts:
    return Accounts(client)


def _theme_of(client: TestClient, headers: dict[str, str]) -> object:
    body = cast(
        "dict[str, object]", client.get("/account", headers=headers).json()
    )

    return body["theme"]


def test_a_new_account_follows_the_system_theme(
    client: TestClient, accounts: Accounts
) -> None:
    assert _theme_of(client, accounts.sign_up()) == "system"


def test_a_chosen_theme_is_remembered(
    client: TestClient, accounts: Accounts
) -> None:
    headers = accounts.sign_up()

    response = client.patch(
        "/account/theme", json={"theme": "dark"}, headers=headers
    )

    assert response.status_code == _OK
    assert cast("dict[str, str]", response.json())["theme"] == "dark"
    assert _theme_of(client, headers) == "dark"


def test_the_theme_can_go_back_to_the_system_one(
    client: TestClient, accounts: Accounts
) -> None:
    headers = accounts.sign_up()

    _ = client.patch("/account/theme", json={"theme": "dark"}, headers=headers)
    _ = client.patch(
        "/account/theme", json={"theme": "system"}, headers=headers
    )

    assert _theme_of(client, headers) == "system"


def test_an_unknown_theme_is_refused(
    client: TestClient, accounts: Accounts
) -> None:
    response = client.patch(
        "/account/theme", json={"theme": "neon"}, headers=accounts.sign_up()
    )

    assert response.status_code == _UNPROCESSABLE_ENTITY


def test_choosing_a_theme_needs_a_token(client: TestClient) -> None:
    response = client.patch("/account/theme", json={"theme": "dark"})

    assert response.status_code == _UNAUTHORIZED
