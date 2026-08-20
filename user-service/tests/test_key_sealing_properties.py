import base64

from hypothesis import given, settings
from hypothesis import strategies as st

from features.account.key_sealing import (
    _derived_key,
    hint_for,
    new_salt,
    seal,
    unseal,
)

_SALT_BYTES = 16
_HINT_CHARACTERS = 4
_SECRETS = st.text(min_size=1, max_size=40)
_PASSWORDS = st.text(min_size=1, max_size=24)


@settings(max_examples=5, deadline=None)
@given(st.integers(min_value=2, max_value=4))
def test_new_salt_property_is_always_fresh_and_the_right_size(
    count: int,
) -> None:
    salts = [new_salt() for _ in range(count)]

    assert len(set(salts)) == count
    assert all(len(base64.b64decode(salt)) == _SALT_BYTES for salt in salts)


@settings(max_examples=5, deadline=None)
@given(_SECRETS, _PASSWORDS)
def test_seal_property_never_repeats_a_ciphertext(
    secret: str, password: str
) -> None:
    salt = new_salt()
    sealed = seal(secret, password, salt)
    sealed_again = seal(secret, password, salt)

    assert sealed != sealed_again
    assert sealed != secret


@settings(max_examples=5, deadline=None)
@given(_SECRETS, _PASSWORDS)
def test_unseal_property_round_trips_a_sealed_secret(
    secret: str, password: str
) -> None:
    salt = new_salt()

    assert unseal(seal(secret, password, salt), password, salt) == secret


@settings(max_examples=5, deadline=None)
@given(_SECRETS, _PASSWORDS, _PASSWORDS)
def test_unseal_property_refuses_the_wrong_password(
    secret: str, password: str, other_password: str
) -> None:
    salt = new_salt()
    sealed = seal(secret, password, salt)
    opened = unseal(sealed, other_password, salt)

    assert opened == (secret if other_password == password else None)


@settings(max_examples=50)
@given(st.text(max_size=40))
def test_hint_for_property_shows_only_the_tail_of_the_secret(
    secret: str,
) -> None:
    hint = hint_for(secret)

    assert secret.endswith(hint)
    assert len(hint) == min(len(secret), _HINT_CHARACTERS)


@settings(max_examples=5, deadline=None)
@given(_PASSWORDS)
def test__derived_key_property_is_the_same_key_every_time(
    password: str,
) -> None:
    salt = new_salt()

    assert _derived_key(password, salt) == _derived_key(password, salt)
