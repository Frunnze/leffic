from collections.abc import Iterator
from typing import cast
from unittest import mock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app_factory import create_app
from features.account import account_router as account_module
from shared.database import Base, get_db
from features.account.events import BrokerUnavailableError
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


@pytest.fixture
def accounts(client: TestClient) -> Accounts:
    return Accounts(client)

def _delete(
    client: TestClient, headers: dict[str, str], password: str
) -> int:
    with mock.patch.object(account_module, "publish"):
        response = client.request(
            "DELETE", "/account", json={"password": password}, headers=headers
        )

    return response.status_code


def test_deleting_the_account_removes_the_login(
    client: TestClient, accounts: Accounts
) -> None:
    headers = accounts.sign_up()

    assert _delete(client, headers, accounts.phrase) == 200

    login = client.post(
        "/login", json={"email": accounts.email, "password": accounts.phrase}
    )

    assert login.status_code == 404


def test_deleting_the_account_needs_the_password(
    client: TestClient, accounts: Accounts
) -> None:
    headers = accounts.sign_up()

    assert _delete(client, headers, accounts.wrong_phrase) == 401


def test_deleting_the_account_takes_its_keys_with_it(
    client: TestClient, accounts: Accounts
) -> None:
    headers = accounts.sign_up()
    accounts.save_key(headers)

    assert _delete(client, headers, accounts.phrase) == 200


def test_deleting_the_account_announces_it(
    client: TestClient, accounts: Accounts
) -> None:
    headers = accounts.sign_up()

    with mock.patch.object(account_module, "publish") as announce:
        response = client.request(
            "DELETE",
            "/account",
            json={"password": accounts.phrase},
            headers=headers,
        )

    assert response.status_code == 200
    assert announce.call_args.args[0] == "user.deleted"
    assert "user_id" in announce.call_args.args[1]


def test_an_account_survives_when_the_announcement_fails(
    client: TestClient, accounts: Accounts
) -> None:
    headers = accounts.sign_up()

    with mock.patch.object(
        account_module, "publish", side_effect=BrokerUnavailableError
    ):
        response = client.request(
            "DELETE",
            "/account",
            json={"password": accounts.phrase},
            headers=headers,
        )

    body = cast("dict[str, str]", response.json())

    assert response.status_code == 503
    assert body["detail"] == "Deletion is unavailable right now. Try again."

    login = client.post(
        "/login", json={"email": accounts.email, "password": accounts.phrase}
    )

    assert login.status_code == 200
