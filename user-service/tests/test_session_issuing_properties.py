import uuid

import jwt
import pytest
from fastapi import HTTPException, Response
from hypothesis import given, settings
from hypothesis import strategies as st

from features.authentication.access import (
    ALGORITHM,
    SECRET_KEY,
    create_refresh_token,
)
from features.authentication.authentication_router import (
    _issue_refresh_cookie,
    _refreshed_user_id,
    _session_payload,
    logout_user,
)
from shared.models import User

_OK = 200
_UNAUTHORIZED = 401
_REFRESH_COOKIE = "refresh_token"
_NAMES = st.text(min_size=1, max_size=16)


def _cookie_value(header: str) -> str:
    return header.split(f"{_REFRESH_COOKIE}=")[1].split(";")[0]


@settings(max_examples=50)
@given(st.uuids(), _NAMES, _NAMES, st.text(min_size=1, max_size=30))
def test__session_payload_property_echoes_the_account_it_describes(
    identifier: uuid.UUID, username: str, email: str, access_token: str
) -> None:
    user = User(id=identifier, username=username, email=email)
    payload = _session_payload(user, access_token)

    assert payload == {
        "user_id": str(identifier),
        "username": username,
        "email": email,
        "access_token": access_token,
    }


@settings(max_examples=50)
@given(st.uuids())
def test__issue_refresh_cookie_property_hides_a_token_for_that_user(
    identifier: uuid.UUID,
) -> None:
    response = Response()
    _issue_refresh_cookie(response, str(identifier))
    header = response.headers["set-cookie"]
    claims = jwt.decode(
        _cookie_value(header), SECRET_KEY, algorithms=[ALGORITHM]
    )

    assert claims["user_id"] == str(identifier)
    assert "httponly" in header.lower()


@settings(max_examples=50)
@given(st.uuids())
def test__refreshed_user_id_property_round_trips_a_refresh_token(
    identifier: uuid.UUID,
) -> None:
    token = create_refresh_token({"user_id": str(identifier)})

    assert _refreshed_user_id(token) == str(identifier)


@settings(max_examples=50)
@given(st.text(max_size=30))
def test__refreshed_user_id_property_refuses_anything_unsigned(
    token: str,
) -> None:
    with pytest.raises(HTTPException) as raised:
        _ = _refreshed_user_id(token)

    assert raised.value.status_code == _UNAUTHORIZED


@settings(max_examples=25)
@given(st.integers(min_value=100, max_value=599))
def test_logout_user_property_always_clears_the_refresh_cookie(
    starting_status: int,
) -> None:
    response = Response(status_code=starting_status)
    body = logout_user(response)

    assert response.status_code == _OK
    assert _cookie_value(response.headers["set-cookie"]) == '""'
    assert "message" in body
