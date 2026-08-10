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

def _change(
    client: TestClient,
    headers: dict[str, str],
    current: str,
    replacement: str,
) -> tuple[int, dict[str, str]]:
    response = client.patch(
        "/account/password",
        json={"current_password": current, "new_password": replacement},
        headers=headers,
    )

    return response.status_code, cast("dict[str, str]", response.json())


def test_changing_the_password_allows_the_new_one(
    client: TestClient, accounts: Accounts
) -> None:
    headers = accounts.sign_up()

    code, _ = _change(client, headers, accounts.phrase, accounts.new_phrase)

    assert code == 200

    login = client.post(
        "/login",
        json={"email": accounts.email, "password": accounts.new_phrase},
    )

    assert login.status_code == 200


def test_the_old_password_stops_working(
    client: TestClient, accounts: Accounts
) -> None:
    headers = accounts.sign_up()

    _ = _change(client, headers, accounts.phrase, accounts.new_phrase)
    login = client.post(
        "/login", json={"email": accounts.email, "password": accounts.phrase}
    )

    assert login.status_code == 404


def test_a_wrong_current_password_is_refused(
    client: TestClient, accounts: Accounts
) -> None:
    headers = accounts.sign_up()

    code, body = _change(
        client, headers, accounts.wrong_phrase, accounts.new_phrase
    )

    assert code == 401
    assert body["detail"] == "That password is not right."


def test_another_accounts_password_does_not_authorize(
    client: TestClient, accounts: Accounts
) -> None:
    owner = accounts.sign_up()
    _ = accounts.sign_up(
        "stranger", "stranger@example.com", accounts.other_phrase
    )

    code, _ = _change(
        client, owner, accounts.other_phrase, accounts.new_phrase
    )

    assert code == 401


def test_a_short_new_password_is_rejected(
    client: TestClient, accounts: Accounts
) -> None:
    headers = accounts.sign_up()

    code, body = _change(client, headers, accounts.phrase, "ab")

    assert code == 422
    assert body["detail"] == "The new password is too short."
