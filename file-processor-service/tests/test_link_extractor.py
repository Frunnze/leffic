from collections.abc import Iterator

import requests
from youtube_transcript_api import NoTranscriptFound

from features.study_units_generation.link_extractor import (
    extract_video_id,
    get_youtube_transcript_auto,
)

_LONG_TEXT = "B" * 250
_VIDEO_ID = "dQw4w9WgXcQ"
_TRANSCRIPT_API_LIST = (
    "features.study_units_generation.link_extractor"
    ".YouTubeTranscriptApi.list"
)


class FakeResponse:
    def __init__(self, html: str, status_code: int = 200) -> None:
        super().__init__()
        self.content: bytes = html.encode("utf-8")
        self.status_code: int = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(f"status {self.status_code}")


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


def test_reads_the_video_id_from_a_watch_url() -> None:
    url = f"https://www.youtube.com/watch?v={_VIDEO_ID}"

    assert extract_video_id(url) == _VIDEO_ID


def test_reads_the_video_id_from_a_short_url() -> None:
    assert extract_video_id(f"https://youtu.be/{_VIDEO_ID}") == _VIDEO_ID


def test_returns_no_video_id_for_another_host() -> None:
    assert extract_video_id("https://example.com/watch?v=x") is None


def test_returns_no_video_id_when_the_query_has_none() -> None:
    assert extract_video_id("https://youtube.com/watch?t=1") is None


def test_no_transcript_without_a_video_id() -> None:
    assert get_youtube_transcript_auto("https://example.com") is None
