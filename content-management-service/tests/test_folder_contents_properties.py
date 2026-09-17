import uuid
from collections.abc import Callable

from hypothesis import given, settings
from hypothesis import strategies as st
from sqlalchemy.orm import Session

from features.file_system.folder_contents import (
    _files,
    _generated_entries,
    _rows_in_folder,
    _source_of,
    _subfolders,
    entries_in,
)
from shared.models import File, FlashcardDeck, Note, Test
from shared.models.mixins import FolderContent, GeneratedContent
from tests.folder_seeding import KINDS, seeded_folder
from tests.support import in_memory_sessions

_COUNTS = st.fixed_dictionaries(
    {kind: st.integers(min_value=0, max_value=3) for kind in KINDS}
)
_SOURCE_KINDS = st.one_of(st.none(), st.sampled_from(["file", "link"]))
_GENERATED_MODELS = (
    (FlashcardDeck, "flashcard_deck"),
    (Test, "test"),
    (Note, "note"),
)
_GENERATED_KINDS = st.sampled_from(_GENERATED_MODELS)
_CONTENT_KINDS = st.sampled_from([*_GENERATED_MODELS, (File, "file")])
_SESSIONS = in_memory_sessions()

Listing = Callable[[Session, str, uuid.UUID], list[dict[str, str]]]
GeneratedKind = tuple[type[GeneratedContent], str]
ContentKind = tuple[type[FolderContent], str]


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
@given(_COUNTS, _CONTENT_KINDS)
def test__rows_in_folder_property_reads_only_that_owners_folder(
    counts: dict[str, int], kind: ContentKind
) -> None:
    model, seeded_kind = kind
    owner = uuid.uuid4()
    stranger = uuid.uuid4()

    with _SESSIONS() as session:
        folder_id = seeded_folder(session, owner, counts)
        mine = _rows_in_folder(session, model, str(folder_id), owner)
        theirs = _rows_in_folder(session, model, str(folder_id), stranger)

    assert len(mine) == counts[seeded_kind]
    assert theirs == []


@settings(max_examples=25, deadline=None)
@given(_COUNTS, _GENERATED_KINDS)
def test__generated_entries_property_labels_every_row_with_its_kind(
    counts: dict[str, int], kind: GeneratedKind
) -> None:
    model, entry_type = kind
    owner = uuid.uuid4()

    with _SESSIONS() as session:
        folder_id = seeded_folder(session, owner, counts)
        rows = _generated_entries(
            session, str(folder_id), owner, model, entry_type
        )

    assert len(rows) == counts[entry_type]
    assert {row["type"] for row in rows} <= {entry_type}


@settings(max_examples=25, deadline=None)
@given(_COUNTS)
def test__files_property_carries_an_extension_on_every_row(
    counts: dict[str, int],
) -> None:
    rows = _listing_for(_files, counts)

    assert len(rows) == counts["file"]
    assert all(row["extension"] == "pdf" for row in rows)


def _listing_for(
    listing: Listing, counts: dict[str, int]
) -> list[dict[str, str]]:
    owner = uuid.uuid4()

    with _SESSIONS() as session:
        folder_id = seeded_folder(session, owner, counts)

        return listing(session, str(folder_id), owner)
