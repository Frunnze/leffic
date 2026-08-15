import uuid

import pytest
from fastapi import HTTPException
from hypothesis import given, settings
from hypothesis import strategies as st

from features.account.account_lookup import account, confirmed_account
from tests.property_support import PHRASE, seeded_user

_NOT_FOUND = 404
_UNAUTHORIZED = 401


@settings(max_examples=25, deadline=None)
@given(st.uuids())
def test_account_property_finds_the_user_it_was_asked_for(
    identifier: uuid.UUID,
) -> None:
    with seeded_user(identifier) as session:
        assert account(session, str(identifier)).id == identifier


@settings(max_examples=25, deadline=None)
@given(st.uuids(), st.uuids())
def test_account_property_reports_an_unknown_user_as_missing(
    identifier: uuid.UUID, stranger: uuid.UUID
) -> None:
    with seeded_user(identifier) as session:
        with pytest.raises(HTTPException) as raised:
            _ = account(session, str(stranger))

    assert raised.value.status_code == _NOT_FOUND


@settings(max_examples=10, deadline=None)
@given(st.uuids())
def test_confirmed_account_property_accepts_the_real_password(
    identifier: uuid.UUID,
) -> None:
    with seeded_user(identifier) as session:
        confirmed = confirmed_account(session, str(identifier), PHRASE)

    assert confirmed.id == identifier


@settings(max_examples=10, deadline=None)
@given(st.uuids(), st.text(min_size=1, max_size=20))
def test_confirmed_account_property_refuses_a_wrong_password(
    identifier: uuid.UUID, attempt: str
) -> None:
    with seeded_user(identifier) as session:
        if attempt == PHRASE:
            return

        with pytest.raises(HTTPException) as raised:
            _ = confirmed_account(session, str(identifier), attempt)

    assert raised.value.status_code == _UNAUTHORIZED
