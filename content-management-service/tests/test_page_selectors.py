import warnings
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


def test_a_content_span_is_not_mistaken_for_a_content_div() -> None:
    html = (
        f'<html><body><span class="content">{_HUGE_TEXT}</span>'
        f'<div class="content">{_OTHER_TEXT}</div>'
        f'<div class="advert">{_HUGE_TEXT}</div></body></html>'
    )

    with mock.patch.object(requests, "get", return_value=FakeResponse(html)):
        assert extract_link_main_content("http://test.com") == _OTHER_TEXT


def test_a_div_without_the_content_class_is_skipped() -> None:
    html = (
        f'<html><body><div class="advert">{_HUGE_TEXT}</div>'
        f'<div class="content">{_OTHER_TEXT}</div></body></html>'
    )

    with mock.patch.object(requests, "get", return_value=FakeResponse(html)):
        assert extract_link_main_content("http://test.com") == _OTHER_TEXT


def test_a_content_span_is_not_mistaken_for_a_content_section() -> None:
    html = (
        f'<html><body><span class="content">{_HUGE_TEXT}</span>'
        f'<section class="content">{_OTHER_TEXT}</section>'
        f'<div class="advert">{_HUGE_TEXT}</div></body></html>'
    )

    with mock.patch.object(requests, "get", return_value=FakeResponse(html)):
        assert extract_link_main_content("http://test.com") == _OTHER_TEXT


def test_the_html_parser_is_pinned_so_bs4_does_not_guess() -> None:
    html = f"<html><body><main>{_LONG_TEXT}</main></body></html>"

    with (
        warnings.catch_warnings(),
        mock.patch.object(requests, "get", return_value=FakeResponse(html)),
    ):
        warnings.simplefilter("error", DeprecationWarning)

        assert extract_link_main_content("http://test.com") == _LONG_TEXT


def test_a_section_without_the_content_class_is_skipped() -> None:
    html = (
        f'<html><body><section class="advert">{_HUGE_TEXT}</section>'
        f'<section class="content">{_OTHER_TEXT}</section>'
        f'<div class="advert">{_HUGE_TEXT}</div></body></html>'
    )

    with mock.patch.object(requests, "get", return_value=FakeResponse(html)):
        assert extract_link_main_content("http://test.com") == _OTHER_TEXT
