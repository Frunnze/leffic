from collections.abc import Iterator
from typing import cast

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app_factory import create_app
from shared.database import Base, get_db
from shared.jwt_secret import ALGORITHM, SECRET_KEY
from tests.support import Accounts, SessionProvider

_CONFLICT = 409
_NOT_FOUND = 404
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


_STRANGER_ID = "6f1c7d4e-0000-4000-8000-0000000000ff"


def _account(client: TestClient, headers: dict[str, str]) -> dict[str, object]:
    return cast(
        "dict[str, object]", client.get("/account", headers=headers).json()
    )


def test_the_account_reports_the_signed_in_identity(
    client: TestClient, accounts: Accounts
) -> None:
    body = _account(client, accounts.sign_up())

    assert body["username"] == accounts.username
    assert body["email"] == accounts.email


def test_the_account_needs_a_token(client: TestClient) -> None:
    assert client.get("/account").status_code == _UNAUTHORIZED


def test_an_unknown_account_is_not_found(client: TestClient) -> None:
    token = jwt.encode(
        {"user_id": _STRANGER_ID}, SECRET_KEY, algorithm=ALGORITHM
    )

    response = client.get(
        "/account", headers={"Authorization": f"Bearer {token}"}
    )
    body = cast("dict[str, str]", response.json())

    assert response.status_code == _NOT_FOUND
    assert body["detail"] == "Account does not exist!"


def test_each_account_reads_its_own_identity(
    client: TestClient, accounts: Accounts
) -> None:
    owner = accounts.sign_up()
    stranger = accounts.sign_up(
        "stranger", "stranger@example.com", accounts.other_phrase
    )

    assert _account(client, owner)["username"] == accounts.username
    assert _account(client, stranger)["username"] == "stranger"


def test_changing_the_username_stores_it(
    client: TestClient, accounts: Accounts
) -> None:
    headers = accounts.sign_up()

    response = client.patch(
        "/account/username", json={"username": "vlad"}, headers=headers
    )

    assert response.status_code == _OK
    assert _account(client, headers)["username"] == "vlad"


def test_a_blank_username_is_rejected(
    client: TestClient, accounts: Accounts
) -> None:
    headers = accounts.sign_up()

    response = client.patch(
        "/account/username", json={"username": "  "}, headers=headers
    )
    body = cast("dict[str, str]", response.json())

    assert response.status_code == _UNPROCESSABLE_ENTITY
    assert body["detail"] == "Username cannot be blank."


def test_a_taken_username_is_rejected(
    client: TestClient, accounts: Accounts
) -> None:
    headers = accounts.sign_up()
    _ = accounts.sign_up("taken", "other@example.com")

    response = client.patch(
        "/account/username", json={"username": "taken"}, headers=headers
    )
    body = cast("dict[str, str]", response.json())

    assert response.status_code == _CONFLICT
    assert body["detail"] == "That username is taken."
