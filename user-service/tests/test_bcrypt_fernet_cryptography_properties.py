from hypothesis import given, settings
from hypothesis import strategies as st

from features.account.bcrypt_fernet_cryptography import (
    BcryptFernetCryptography,
)
from features.account.key_sealing import new_salt

_BCRYPT_SAFE_TEXT = st.text(
    alphabet=st.characters(min_codepoint=32, max_codepoint=126),
    min_size=1,
    max_size=40,
)
_KEYS = st.text(min_size=1, max_size=40)
_CRYPTOGRAPHY = BcryptFernetCryptography()


@settings(max_examples=10, deadline=None)
@given(_BCRYPT_SAFE_TEXT)
def test_hash_password_property_keeps_only_a_verifiable_digest(
    password: str,
) -> None:
    hashed_password = _CRYPTOGRAPHY.hash_password(password)

    assert hashed_password != password
    assert _CRYPTOGRAPHY.verify_password(password, hashed_password) is True


@settings(max_examples=10, deadline=None)
@given(_BCRYPT_SAFE_TEXT, _BCRYPT_SAFE_TEXT)
def test_verify_password_property_accepts_only_the_hashed_password(
    password: str, attempted_password: str
) -> None:
    hashed_password = _CRYPTOGRAPHY.hash_password(password)
    is_accepted = _CRYPTOGRAPHY.verify_password(
        attempted_password, hashed_password
    )

    assert is_accepted is (attempted_password == password)


@settings(max_examples=5, deadline=None)
@given(_KEYS, _BCRYPT_SAFE_TEXT)
def test_seal_key_property_round_trips_through_open_key(
    key: str, password: str
) -> None:
    salt = new_salt()
    sealed_key = _CRYPTOGRAPHY.seal_key(key, password, salt)

    assert sealed_key != key
    assert _CRYPTOGRAPHY.open_key(sealed_key, password, salt) == key


@settings(max_examples=5, deadline=None)
@given(_KEYS, _BCRYPT_SAFE_TEXT, _BCRYPT_SAFE_TEXT)
def test_open_key_property_opens_only_with_the_sealing_password(
    key: str, password: str, attempted_password: str
) -> None:
    salt = new_salt()
    sealed_key = _CRYPTOGRAPHY.seal_key(key, password, salt)
    opened_key = _CRYPTOGRAPHY.open_key(sealed_key, attempted_password, salt)
    expected_key = key if attempted_password == password else None

    assert opened_key == expected_key
