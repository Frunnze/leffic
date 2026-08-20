import uuid
from collections.abc import Callable

from hypothesis import given, settings
from hypothesis import strategies as st
from sqlalchemy.orm import Session

from features.file_system.folder_contents import (
    _files,
    _flashcard_decks,
    _notes,
    _source_of,
    _subfolders,
    _tests,
    entries_in,
)
from shared.models import FlashcardDeck
from tests.folder_seeding import KINDS, seeded_folder
from tests.support import in_memory_sessions

_COUNTS = st.fixed_dictionaries(
    {kind: st.integers(min_value=0, max_value=3) for kind in KINDS}
)
_SOURCE_KINDS = st.one_of(st.none(), st.sampled_from(["file", "link"]))
_SESSIONS = in_memory_sessions()

Listing = Callable[[Session, str, uuid.UUID], list[dict[str, str]]]


@settings(max_examples=25, deadline=None)
@given(_SOURCE_KINDS, st.one_of(st.none(), st.text(max_size=8)))
def test__source_of_property_reports_a_reference_only_with_a_kind(
    source_kind: str | None, reference: str | None
) -> None:
    row = FlashcardDeck(source_kind=source_kind, source_reference=reference)
    described = _source_of(row)

    if source_kind is None:
        assert described == {}
    else:
        assert described["source_kind"] == source_kind
        assert described["source_reference"] == (reference or "")


@settings(max_examples=25, deadline=None)
@given(_COUNTS)
def test_entries_in_property_returns_every_seeded_entry_once(
    counts: dict[str, int],
) -> None:
    owner = uuid.uuid4()

    with _SESSIONS() as session:
        folder_id = seeded_folder(session, owner, counts)
        entries = entries_in(session, str(folder_id), str(owner))

    assert len(entries) == sum(counts.values())
    assert len({entry["id"] for entry in entries}) == len(entries)


@settings(max_examples=25, deadline=None)
@given(_COUNTS, _COUNTS)
def test_entries_in_property_never_shows_another_owners_content(
    mine: dict[str, int], theirs: dict[str, int]
) -> None:
    owner = uuid.uuid4()
    stranger = uuid.uuid4()

    with _SESSIONS() as session:
        folder_id = seeded_folder(session, owner, mine)
        _ = seeded_folder(session, stranger, theirs)
        seen = entries_in(session, str(folder_id), str(stranger))

    assert seen == []


@settings(max_examples=25, deadline=None)
@given(_COUNTS)
def test__subfolders_property_labels_every_row_as_a_folder(
    counts: dict[str, int],
) -> None:
    rows = _listing_for(_subfolders, counts)

    assert len(rows) == counts["folder"]
    assert {row["type"] for row in rows} <= {"folder"}


@settings(max_examples=25, deadline=None)
@given(_COUNTS)
def test__flashcard_decks_property_labels_every_row_as_a_deck(
    counts: dict[str, int],
) -> None:
    rows = _listing_for(_flashcard_decks, counts)

    assert len(rows) == counts["flashcard_deck"]
    assert {row["type"] for row in rows} <= {"flashcard_deck"}


@settings(max_examples=25, deadline=None)
@given(_COUNTS)
def test__tests_property_labels_every_row_as_a_test(
    counts: dict[str, int],
) -> None:
    rows = _listing_for(_tests, counts)

    assert len(rows) == counts["test"]
    assert {row["type"] for row in rows} <= {"test"}


@settings(max_examples=25, deadline=None)
@given(_COUNTS)
def test__files_property_carries_an_extension_on_every_row(
    counts: dict[str, int],
) -> None:
    rows = _listing_for(_files, counts)

    assert len(rows) == counts["file"]
    assert all(row["extension"] == "pdf" for row in rows)


@settings(max_examples=25, deadline=None)
@given(_COUNTS)
def test__notes_property_labels_every_row_as_a_note(
    counts: dict[str, int],
) -> None:
    rows = _listing_for(_notes, counts)

    assert len(rows) == counts["note"]
    assert {row["type"] for row in rows} <= {"note"}


def _listing_for(
    listing: Listing, counts: dict[str, int]
) -> list[dict[str, str]]:
    owner = uuid.uuid4()

    with _SESSIONS() as session:
        folder_id = seeded_folder(session, owner, counts)

        return listing(session, str(folder_id), owner)
