import uuid

from hypothesis import given, settings
from hypothesis import strategies as st
from sqlalchemy.orm import Session

from features.authentication.database_user_registry import (
    DatabaseUserRegistry,
)
from shared.models import User
from tests.property_support import seeded_user

_STRANGER_SUFFIX = "-stranger"


def _seeded_account(session: Session, identifier: uuid.UUID) -> User:
    seeded_account = session.get(User, identifier)

    if seeded_account is None:
        raise LookupError(identifier)

    return seeded_account


@settings(max_examples=25, deadline=None)
@given(st.uuids())
def test_user_named_property_finds_only_the_username_asked_for(
    identifier: uuid.UUID,
) -> None:
    with seeded_user(identifier) as session:
        registry = DatabaseUserRegistry(session)
        username = _seeded_account(session, identifier).username
        found_user = registry.user_named(username)
        stranger = registry.user_named(username + _STRANGER_SUFFIX)

    assert found_user is not None
    assert found_user.id == identifier
    assert stranger is None


@settings(max_examples=25, deadline=None)
@given(st.uuids())
def test_user_with_email_property_finds_only_the_email_asked_for(
    identifier: uuid.UUID,
) -> None:
    with seeded_user(identifier) as session:
        registry = DatabaseUserRegistry(session)
        email = _seeded_account(session, identifier).email
        found_user = registry.user_with_email(email)
        stranger = registry.user_with_email(email + _STRANGER_SUFFIX)

    assert found_user is not None
    assert found_user.id == identifier
    assert stranger is None


@settings(max_examples=25, deadline=None)
@given(st.uuids(), st.uuids())
def test_register_property_makes_the_new_user_findable(
    identifier: uuid.UUID, newcomer_marker: uuid.UUID
) -> None:
    newcomer = User(
        username=f"newcomer-{newcomer_marker.hex}",
        email=f"newcomer-{newcomer_marker.hex}@example.com",
        hashed_password="hashed",
    )

    with seeded_user(identifier) as session:
        registry = DatabaseUserRegistry(session)
        registry.register(newcomer)
        found_by_name = registry.user_named(newcomer.username)
        found_by_email = registry.user_with_email(newcomer.email)

    assert found_by_name is newcomer
    assert found_by_email is newcomer
