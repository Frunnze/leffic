from collections.abc import Iterator
from unittest import mock

import requests
from youtube_transcript_api import NoTranscriptFound

from features.study_units_generation.link_extractor import (
    extract_link_main_content,
)
from tests.support import FakeHTTPError

_BAD_REQUEST = 400

_LONG_TEXT = "B" * 250
_OTHER_TEXT = "E" * 260
_HUGE_TEXT = "F" * 400
_VIDEO_ID = "dQw4w9WgXcQ"
_TRANSCRIPT_API_LIST = (
    "features.study_units_generation.link_extractor.YouTubeTranscriptApi.list"
)


class FakeResponse:
    def __init__(self, html: str, status_code: int = 200) -> None:
        super().__init__()
        self.text: str = html
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

    def fetch(self) -> list[FakeSnippet]:
        return [FakeSnippet(self.text)]


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


def test_reads_the_article_element() -> None:
    html = f"<html><body><article>{_LONG_TEXT}</article></body></html>"

    with mock.patch.object(requests, "get", return_value=FakeResponse(html)):
        assert extract_link_main_content("http://test.com") == _LONG_TEXT


def test_reads_a_content_div_when_there_is_no_article() -> None:
    html = (
        f'<html><body><div class="main-content">{_LONG_TEXT}'
        "</div></body></html>"
    )

    with mock.patch.object(requests, "get", return_value=FakeResponse(html)):
        assert extract_link_main_content("http://test.com") == _LONG_TEXT


def test_falls_back_to_the_largest_div() -> None:
    html = f"<html><body><div>short</div><div>{_LONG_TEXT}</div></body></html>"

    with mock.patch.object(requests, "get", return_value=FakeResponse(html)):
        assert extract_link_main_content("http://test.com") == _LONG_TEXT
