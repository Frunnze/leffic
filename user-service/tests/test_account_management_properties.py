import uuid
from typing import cast
from unittest import mock

import pytest
from fastapi import HTTPException
from hypothesis import given, settings
from hypothesis import strategies as st

from features.account import account_router as account_module
from features.account.account_router import _announce_deletion
from shared.events import BrokerUnavailableError
from tests.property_support import (
    PHRASE,
    fresh_credentials,
    property_client,
    signed_up_headers,
)

_OK = 200
_NOT_FOUND = 404
_UNPROCESSABLE = 422
_UNAVAILABLE = 503
_THEMES = st.sampled_from(["system", "light", "dark"])
_BLANK_NAMES = st.sampled_from(["", " ", "\t", "   \n "])
_CLIENT = property_client()


def _account_body(headers: dict[str, str]) -> dict[str, str]:
    response = _CLIENT.get("/account", headers=headers)

    return cast("dict[str, str]", response.json())


@settings(max_examples=10, deadline=None)
@given(st.uuids())
def test_read_account_property_describes_the_signed_in_account(
    marker: uuid.UUID,
) -> None:
    credentials = fresh_credentials(marker, "read")
    headers = signed_up_headers(_CLIENT, marker, "read")
    body = _account_body(headers)

    assert body["username"] == credentials["username"]
    assert body["email"] == credentials["email"]
    assert "hashed_password" not in body


@settings(max_examples=10, deadline=None)
@given(st.uuids())
def test_change_username_property_shows_the_new_name_afterwards(
    marker: uuid.UUID,
) -> None:
    headers = signed_up_headers(_CLIENT, marker, "rename")
    chosen = f"renamed-{marker.hex}"
    response = _CLIENT.patch(
        "/account/username", json={"username": chosen}, headers=headers
    )

    assert response.status_code == _OK
    assert _account_body(headers)["username"] == chosen


@settings(max_examples=10, deadline=None)
@given(st.uuids(), _BLANK_NAMES)
def test_change_username_property_refuses_a_blank_name(
    marker: uuid.UUID, blank: str
) -> None:
    headers = signed_up_headers(_CLIENT, marker, f"blank{len(blank)}")
    response = _CLIENT.patch(
        "/account/username", json={"username": blank}, headers=headers
    )

    assert response.status_code == _UNPROCESSABLE


@settings(max_examples=10, deadline=None)
@given(st.uuids())
def test_change_password_property_retires_the_previous_password(
    marker: uuid.UUID,
) -> None:
    credentials = fresh_credentials(marker, "repassword")
    headers = signed_up_headers(_CLIENT, marker, "repassword")
    replacement = f"phrase-{marker.hex}"
    changed = _CLIENT.patch(
        "/account/password",
        json={"current_password": PHRASE, "new_password": replacement},
        headers=headers,
    )
    old_login = _CLIENT.post(
        "/login",
        json={"email": credentials["email"], "password": PHRASE},
    )
    new_login = _CLIENT.post(
        "/login",
        json={"email": credentials["email"], "password": replacement},
    )

    assert changed.status_code == _OK
    assert old_login.status_code == _NOT_FOUND
    assert new_login.status_code == _OK


@settings(max_examples=10, deadline=None)
@given(st.uuids())
def test_delete_account_property_leaves_nothing_to_read(
    marker: uuid.UUID,
) -> None:
    headers = signed_up_headers(_CLIENT, marker, "delete")

    with mock.patch.object(account_module, "publish"):
        removed = _CLIENT.request(
            "DELETE", "/account", json={"password": PHRASE}, headers=headers
        )

    assert removed.status_code == _OK
    assert _CLIENT.get("/account", headers=headers).status_code == _NOT_FOUND


@settings(max_examples=25)
@given(st.uuids())
def test__announce_deletion_property_reports_an_unreachable_broker(
    marker: uuid.UUID,
) -> None:
    with mock.patch.object(
        account_module, "publish", side_effect=BrokerUnavailableError
    ):
        with pytest.raises(HTTPException) as raised:
            _announce_deletion(str(marker))

    assert raised.value.status_code == _UNAVAILABLE


@settings(max_examples=10, deadline=None)
@given(st.uuids(), _THEMES)
def test_choose_theme_property_remembers_the_theme_that_was_picked(
    marker: uuid.UUID, theme: str
) -> None:
    headers = signed_up_headers(_CLIENT, marker, f"theme{theme}")
    response = _CLIENT.patch(
        "/account/theme", json={"theme": theme}, headers=headers
    )

    assert response.status_code == _OK
    assert _account_body(headers)["theme"] == theme
