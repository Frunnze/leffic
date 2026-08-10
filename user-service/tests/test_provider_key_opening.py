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

def test_a_sealed_key_opens_with_the_right_password(
    accounts: Accounts,
) -> None:
    headers = accounts.sign_up()
    accounts.save_key(headers)

    opened = accounts.open_key(headers)
    body = cast("dict[str, str]", opened["body"])

    assert opened["status"] == 200
    assert body["key"] == accounts.openai_key


def test_opening_a_key_needs_the_password(accounts: Accounts) -> None:
    headers = accounts.sign_up()
    accounts.save_key(headers)

    opened = accounts.open_key(headers, password=accounts.wrong_phrase)

    assert opened["status"] == 401


def test_opening_a_missing_key_is_not_found(accounts: Accounts) -> None:
    headers = accounts.sign_up()

    assert accounts.open_key(headers, provider="gemini")["status"] == 404


def test_each_provider_keeps_its_own_key(accounts: Accounts) -> None:
    headers = accounts.sign_up()
    accounts.save_key(headers)
    accounts.save_key(headers, provider="gemini", key=accounts.gemini_key)

    opened = accounts.open_key(headers, provider="gemini")
    body = cast("dict[str, str]", opened["body"])

    assert body["key"] == accounts.gemini_key


def test_one_account_never_opens_another_accounts_key(
    accounts: Accounts,
) -> None:
    owner = accounts.sign_up()
    accounts.save_key(owner)
    stranger = accounts.sign_up(
        "stranger", "stranger@example.com", accounts.other_phrase
    )
    accounts.save_key(
        stranger,
        key="sk-live-33333333333333334Qd1",
        password=accounts.other_phrase,
    )

    opened = accounts.open_key(stranger, password=accounts.other_phrase)
    body = cast("dict[str, str]", opened["body"])

    assert body["key"] == "sk-live-33333333333333334Qd1"


def test_a_key_sealed_under_an_old_password_will_not_open(
    client: TestClient, accounts: Accounts
) -> None:
    headers = accounts.sign_up()
    accounts.save_key(headers)
    _ = client.patch(
        "/account/password",
        json={
            "current_password": accounts.phrase,
            "new_password": accounts.new_phrase,
        },
        headers=headers,
    )

    opened = accounts.open_key(headers, password=accounts.new_phrase)
    body = cast("dict[str, str]", opened["body"])

    assert opened["status"] == 409
    assert body["detail"] == "This key was sealed with an earlier password."


def test_a_provider_without_a_key_is_not_found_even_when_others_exist(
    accounts: Accounts,
) -> None:
    headers = accounts.sign_up()
    accounts.save_key(headers)

    assert accounts.open_key(headers, provider="gemini")["status"] == 404


def test_a_stranger_cannot_open_a_key_they_never_saved(
    accounts: Accounts,
) -> None:
    owner = accounts.sign_up()
    accounts.save_key(owner)
    stranger = accounts.sign_up(
        "stranger", "stranger@example.com", accounts.other_phrase
    )

    opened = accounts.open_key(stranger, password=accounts.other_phrase)

    assert opened["status"] == 404
