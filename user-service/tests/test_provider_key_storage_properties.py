import uuid
from typing import cast

from hypothesis import given, settings
from hypothesis import strategies as st

from features.account.provider_key_router import _keys_of, _saved_key
from tests.property_support import (
    PHRASE,
    property_client,
    seeded_provider_key,
    signed_up_headers,
)

_OK = 200
_NOT_FOUND = 404
_HINT_CHARACTERS = 4
_PROVIDERS = st.sampled_from(["openai", "gemini"])
_KEYS = st.text(
    alphabet=st.characters(min_codepoint=48, max_codepoint=122),
    min_size=8,
    max_size=24,
)
_CLIENT = property_client()


def _saved(headers: dict[str, str], provider: str, key: str) -> int:
    response = _CLIENT.put(
        "/account/provider-keys",
        json={"provider": provider, "key": key, "password": PHRASE},
        headers=headers,
    )

    return response.status_code


@settings(max_examples=10, deadline=None)
@given(st.uuids(), _PROVIDERS, _KEYS)
def test_save_provider_key_property_reports_only_the_tail_as_a_hint(
    marker: uuid.UUID, provider: str, key: str
) -> None:
    headers = signed_up_headers(_CLIENT, marker, f"save{provider}")
    response = _CLIENT.put(
        "/account/provider-keys",
        json={"provider": provider, "key": key, "password": PHRASE},
        headers=headers,
    )
    body = cast("dict[str, str]", response.json())

    assert response.status_code == _OK
    assert body["hint"] == key[-_HINT_CHARACTERS:]


@settings(max_examples=10, deadline=None)
@given(st.uuids(), _PROVIDERS, _KEYS)
def test_open_provider_key_property_round_trips_the_saved_key(
    marker: uuid.UUID, provider: str, key: str
) -> None:
    headers = signed_up_headers(_CLIENT, marker, f"open{provider}")
    _ = _saved(headers, provider, key)
    response = _CLIENT.post(
        f"/account/provider-keys/{provider}/open",
        json={"password": PHRASE},
        headers=headers,
    )
    body = cast("dict[str, str]", response.json())

    assert response.status_code == _OK
    assert body["key"] == key


@settings(max_examples=10, deadline=None)
@given(st.uuids(), _PROVIDERS, _KEYS)
def test_read_provider_keys_property_never_hands_back_the_secret(
    marker: uuid.UUID, provider: str, key: str
) -> None:
    headers = signed_up_headers(_CLIENT, marker, f"list{provider}")
    _ = _saved(headers, provider, key)
    response = _CLIENT.get("/account/provider-keys", headers=headers)
    listed = cast(
        "dict[str, list[dict[str, object]]]", response.json()
    )["provider_keys"]

    assert [entry["provider"] for entry in listed] == [provider]
    assert listed[0]["hint"] == key[-_HINT_CHARACTERS:]
    assert all(
        key not in str(value)
        for entry in listed
        for value in entry.values()
    )


@settings(max_examples=10, deadline=None)
@given(st.uuids(), _PROVIDERS, _KEYS)
def test_delete_provider_key_property_leaves_nothing_to_open(
    marker: uuid.UUID, provider: str, key: str
) -> None:
    headers = signed_up_headers(_CLIENT, marker, f"drop{provider}")
    _ = _saved(headers, provider, key)
    removed = _CLIENT.delete(
        f"/account/provider-keys/{provider}", headers=headers
    )
    opened = _CLIENT.post(
        f"/account/provider-keys/{provider}/open",
        json={"password": PHRASE},
        headers=headers,
    )

    assert removed.status_code == _OK
    assert opened.status_code == _NOT_FOUND


@settings(max_examples=25, deadline=None)
@given(st.lists(_PROVIDERS, unique=True, max_size=2))
def test__keys_of_property_never_reaches_another_owners_keys(
    providers: list[str],
) -> None:
    owner = uuid.uuid4()
    stranger = uuid.uuid4()

    with seeded_provider_key(owner, providers) as session:
        assert len(_keys_of(session, str(owner))) == len(providers)
        assert _keys_of(session, str(stranger)) == []


@settings(max_examples=25, deadline=None)
@given(_PROVIDERS)
def test__saved_key_property_finds_only_the_provider_asked_for(
    provider: str,
) -> None:
    owner = uuid.uuid4()

    with seeded_provider_key(owner, [provider]) as session:
        found = _saved_key(session, str(owner), provider)

        assert found is not None
        assert found.provider == provider
        assert _saved_key(session, str(owner), "missing-provider") is None
