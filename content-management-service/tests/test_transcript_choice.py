from collections.abc import Iterator
from contextlib import AbstractContextManager
from typing import override
from unittest import mock

from youtube_transcript_api import NoTranscriptFound, TranscriptsDisabled

from features.study_units_generation.link_extractor import (
    extract_video_id,
    get_youtube_transcript_auto,
)
from tests.support import FakeHTTPError

_BAD_REQUEST = 400

_LONG_TEXT = "B" * 250
_VIDEO_ID = "dQw4w9WgXcQ"
_TRANSCRIPT_API_LIST = (
    "features.study_units_generation.link_extractor.YouTubeTranscriptApi.list"
)


class FakeResponse:
    def __init__(self, html: str, status_code: int = 200) -> None:
        super().__init__()
        self.content: bytes = html.encode("utf-8")
        self.status_code: int = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= _BAD_REQUEST:
            raise FakeHTTPError(self.status_code)


class FakeSnippet:
    def __init__(self, text: str) -> None:
        super().__init__()
        self.text: str = text


class FakeTranscript:
    def __init__(self, text: str, *, is_generated: bool) -> None:
        super().__init__()
        self.text: str = text
        self.is_generated: bool = is_generated
        self.extra_snippets: list[str] = []

    def fetch(self) -> list[FakeSnippet]:
        snippets = [self.text, *self.extra_snippets]

        return [FakeSnippet(snippet) for snippet in snippets]


class FakeTranscriptList:
    def __init__(
        self,
        transcripts: list[FakeTranscript],
        *,
        manual_found: FakeTranscript | None = None,
        generated_found: FakeTranscript | None = None,
    ) -> None:
        super().__init__()
        self.transcripts: list[FakeTranscript] = transcripts
        self.manual_found: FakeTranscript | None = manual_found
        self.generated_found: FakeTranscript | None = generated_found

    def __iter__(self) -> Iterator[FakeTranscript]:
        return iter(self.transcripts)

    def find_manually_created_transcript(
        self, language_codes: list[str]
    ) -> FakeTranscript:
        if self.manual_found is None:
            raise NoTranscriptFound(_VIDEO_ID, language_codes, {})

        return self.manual_found

    def find_generated_transcript(
        self, language_codes: list[str]
    ) -> FakeTranscript:
        if self.generated_found is None:
            raise NoTranscriptFound(_VIDEO_ID, language_codes, {})

        return self.generated_found


class RecordingTranscriptList(FakeTranscriptList):
    def __init__(self) -> None:
        super().__init__([], manual_found=None)
        self.asked: list[list[str]] = []

    @override
    def find_manually_created_transcript(
        self, language_codes: list[str]
    ) -> FakeTranscript:
        self.asked.append(language_codes)

        return super().find_manually_created_transcript(language_codes)


def _patch_transcripts(
    transcript_list: object,
) -> AbstractContextManager[object]:
    return mock.patch(
        _TRANSCRIPT_API_LIST,
        return_value=transcript_list,
    )


def test_prefers_a_manually_created_transcript() -> None:
    manual = FakeTranscript("manual words", is_generated=False)
    listing = FakeTranscriptList([], manual_found=manual)

    with _patch_transcripts(listing):
        transcript = get_youtube_transcript_auto(
            f"https://youtu.be/{_VIDEO_ID}"
        )

    assert transcript == "manual words"


def test_falls_back_to_a_generated_transcript() -> None:
    generated = FakeTranscript("generated words", is_generated=True)
    listing = FakeTranscriptList([], generated_found=generated)

    with _patch_transcripts(listing):
        transcript = get_youtube_transcript_auto(
            f"https://youtu.be/{_VIDEO_ID}"
        )

    assert transcript == "generated words"


def test_falls_back_to_any_manual_transcript() -> None:
    any_manual = FakeTranscript("any manual", is_generated=False)
    listing = FakeTranscriptList([any_manual])

    with _patch_transcripts(listing):
        transcript = get_youtube_transcript_auto(
            f"https://youtu.be/{_VIDEO_ID}"
        )

    assert transcript == "any manual"


def test_falls_back_to_any_generated_transcript() -> None:
    any_generated = FakeTranscript("any generated", is_generated=True)
    listing = FakeTranscriptList([any_generated])

    with _patch_transcripts(listing):
        transcript = get_youtube_transcript_auto(
            f"https://youtu.be/{_VIDEO_ID}"
        )

    assert transcript == "any generated"


def test_returns_nothing_when_no_transcript_exists() -> None:
    listing = FakeTranscriptList([])

    with _patch_transcripts(listing):
        transcript = get_youtube_transcript_auto(
            f"https://youtu.be/{_VIDEO_ID}"
        )

    assert transcript is None


def test_returns_nothing_when_transcripts_are_disabled() -> None:
    with mock.patch(
        _TRANSCRIPT_API_LIST,
        side_effect=TranscriptsDisabled(_VIDEO_ID),
    ):
        transcript = get_youtube_transcript_auto(
            f"https://youtu.be/{_VIDEO_ID}"
        )

    assert transcript is None


def test_the_short_url_path_only_strips_slashes() -> None:
    assert extract_video_id("https://youtu.be//Xabc") == "Xabc"


def test_snippets_are_joined_with_single_spaces() -> None:
    manual = FakeTranscript("one", is_generated=False)
    manual.extra_snippets = ["two"]
    listing = FakeTranscriptList([], manual_found=manual)

    with _patch_transcripts(listing):
        transcript = get_youtube_transcript_auto(
            f"https://youtu.be/{_VIDEO_ID}"
        )

    assert transcript == "one two"
