import uuid
from typing import cast

from hypothesis import given, settings
from hypothesis import strategies as st

from tests.property_support import fresh_credentials, property_client

_OK = 200
_CONFLICT = 409
_UNPROCESSABLE = 422
_NUL_BYTE = chr(0)
_CLIENT = property_client()


def _signed_up(marker: uuid.UUID, scenario: str) -> dict[str, str]:
    credentials = fresh_credentials(marker, scenario)
    response = _CLIENT.post("/sign-up", json=credentials)

    return cast("dict[str, str]", response.json())


@settings(max_examples=10, deadline=None)
@given(st.uuids())
def test_register_user_property_returns_the_account_it_just_created(
    marker: uuid.UUID,
) -> None:
    credentials = fresh_credentials(marker, "created")
    body = _signed_up(marker, "created")

    assert body["username"] == credentials["username"]
    assert body["email"] == credentials["email"]
    assert uuid.UUID(body["user_id"])


@settings(max_examples=10, deadline=None)
@given(st.uuids())
def test_register_user_property_refuses_a_username_taken_already(
    marker: uuid.UUID,
) -> None:
    credentials = fresh_credentials(marker, "duplicate")
    _ = _CLIENT.post("/sign-up", json=credentials)
    again = _CLIENT.post("/sign-up", json=credentials)

    assert again.status_code == _CONFLICT


@settings(max_examples=10, deadline=None)
@given(st.uuids())
def test_login_user_property_returns_the_same_account_that_signed_up(
    marker: uuid.UUID,
) -> None:
    credentials = fresh_credentials(marker, "login")
    signed_up = _signed_up(marker, "login")
    response = _CLIENT.post(
        "/login",
        json={
            "email": credentials["email"],
            "password": credentials["password"],
        },
    )
    body = cast("dict[str, str]", response.json())

    assert response.status_code == _OK
    assert body["user_id"] == signed_up["user_id"]


@settings(max_examples=10, deadline=None)
@given(st.uuids())
def test_refresh_token_property_renews_access_for_the_signed_in_user(
    marker: uuid.UUID,
) -> None:
    signed_up = _signed_up(marker, "refresh")
    response = _CLIENT.post("/refresh-token")
    body = cast("dict[str, str]", response.json())

    assert response.status_code == _OK
    assert body["user_id"] == signed_up["user_id"]
    assert body["access_token"]


@settings(max_examples=10, deadline=None)
@given(st.uuids())
def test_register_user_property_refuses_a_password_with_a_nul_byte(
    marker: uuid.UUID,
) -> None:
    credentials = fresh_credentials(marker, "nulbyte")
    credentials["password"] = f"good{_NUL_BYTE}phrase"
    response = _CLIENT.post("/sign-up", json=credentials)

    assert response.status_code == _UNPROCESSABLE
