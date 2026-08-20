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

_NOT_FOUND = 404
_OK = 200
_UNAUTHORIZED = 401
_UNPROCESSABLE_ENTITY = 422
_MONTHLY_LIMIT_CENTS = 2000


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


def test_provider_keys_start_empty(accounts: Accounts) -> None:
    assert accounts.keys(accounts.sign_up()) == []


def test_saving_a_key_returns_only_its_hint(
    client: TestClient, accounts: Accounts
) -> None:
    headers = accounts.sign_up()

    response = client.put(
        "/account/provider-keys",
        json={
            "provider": "openai",
            "key": accounts.openai_key,
            "password": accounts.phrase,
            "monthly_limit_cents": _MONTHLY_LIMIT_CENTS,
        },
        headers=headers,
    )
    body = cast("dict[str, object]", response.json())

    assert body["hint"] == accounts.openai_key[-4:]
    assert accounts.openai_key not in response.text


def test_a_saved_key_is_listed_with_its_limit(
    client: TestClient, accounts: Accounts
) -> None:
    headers = accounts.sign_up()
    _ = client.put(
        "/account/provider-keys",
        json={
            "provider": "openai",
            "key": accounts.openai_key,
            "password": accounts.phrase,
            "monthly_limit_cents": _MONTHLY_LIMIT_CENTS,
        },
        headers=headers,
    )

    listed = accounts.keys(headers)

    assert listed[0]["provider"] == "openai"
    assert listed[0]["monthly_limit_cents"] == _MONTHLY_LIMIT_CENTS
    assert listed[0]["spent_cents"] == 0


def test_saving_a_key_twice_replaces_it(accounts: Accounts) -> None:
    headers = accounts.sign_up()
    accounts.save_key(headers)
    accounts.save_key(headers, key="sk-live-11111111111111119Zb7")

    listed = accounts.keys(headers)

    assert len(listed) == 1
    assert listed[0]["hint"] == "9Zb7"


def test_saving_a_key_needs_the_password(
    client: TestClient, accounts: Accounts
) -> None:
    headers = accounts.sign_up()

    response = client.put(
        "/account/provider-keys",
        json={
            "provider": "openai",
            "key": accounts.openai_key,
            "password": accounts.wrong_phrase,
        },
        headers=headers,
    )

    assert response.status_code == _UNAUTHORIZED


def test_an_unknown_provider_is_rejected(
    client: TestClient, accounts: Accounts
) -> None:
    headers = accounts.sign_up()

    response = client.put(
        "/account/provider-keys",
        json={
            "provider": "sorcery",
            "key": accounts.openai_key,
            "password": accounts.phrase,
        },
        headers=headers,
    )
    body = cast("dict[str, str]", response.json())

    assert response.status_code == _UNPROCESSABLE_ENTITY
    assert body["detail"] == "That AI provider is not supported."


def test_a_blank_key_is_rejected(
    client: TestClient, accounts: Accounts
) -> None:
    headers = accounts.sign_up()

    response = client.put(
        "/account/provider-keys",
        json={
            "provider": "openai",
            "key": "   ",
            "password": accounts.phrase,
        },
        headers=headers,
    )
    body = cast("dict[str, str]", response.json())

    assert response.status_code == _UNPROCESSABLE_ENTITY
    assert body["detail"] == "The key cannot be blank."


def test_removing_a_key_empties_the_list(
    client: TestClient, accounts: Accounts
) -> None:
    headers = accounts.sign_up()
    accounts.save_key(headers)

    response = client.delete("/account/provider-keys/openai", headers=headers)

    assert response.status_code == _OK
    assert accounts.keys(headers) == []


def test_removing_a_missing_key_is_not_found(
    client: TestClient, accounts: Accounts
) -> None:
    headers = accounts.sign_up()

    response = client.delete("/account/provider-keys/gemini", headers=headers)
    body = cast("dict[str, str]", response.json())

    assert response.status_code == _NOT_FOUND
    assert body["detail"] == "No key is saved for that provider."


def test_one_account_never_sees_another_accounts_keys(
    accounts: Accounts,
) -> None:
    owner = accounts.sign_up()
    accounts.save_key(owner)
    stranger = accounts.sign_up(
        "stranger", "stranger@example.com", accounts.other_phrase
    )

    assert accounts.keys(stranger) == []
