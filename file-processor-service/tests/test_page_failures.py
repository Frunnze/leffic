from collections.abc import Iterator
from unittest import mock

import requests
from youtube_transcript_api import NoTranscriptFound

from features.study_units_generation.link_extractor import (
    extract_link_main_content,
)

_LONG_TEXT = "B" * 250
_OTHER_TEXT = "E" * 260
_HUGE_TEXT = "F" * 400
_VIDEO_ID = "dQw4w9WgXcQ"
_TRANSCRIPT_API_LIST = (
    "features.study_units_generation.link_extractor"
    ".YouTubeTranscriptApi.list"
)


class FakeResponse:
    def __init__(self, html: str, status_code: int = 200) -> None:
        super().__init__()
        self.text: str = html
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


def test_returns_nothing_when_the_page_is_too_short() -> None:
    html = "<html><body><div>tiny</div></body></html>"

    with mock.patch.object(
        requests, "get", return_value=FakeResponse(html)
    ):
        assert extract_link_main_content("http://test.com") is None


def test_returns_nothing_when_the_page_has_no_divs() -> None:
    with mock.patch.object(
        requests, "get", return_value=FakeResponse("<html></html>")
    ):
        assert extract_link_main_content("http://test.com") is None


def test_returns_nothing_on_a_network_failure() -> None:
    with mock.patch.object(
        requests, "get", side_effect=requests.ConnectionError("down")
    ):
        assert extract_link_main_content("http://test.com") is None


def test_returns_nothing_on_an_error_status() -> None:
    with mock.patch.object(
        requests, "get", return_value=FakeResponse("<html></html>", 404)
    ):
        assert extract_link_main_content("http://test.com") is None


def test_passes_custom_headers_through() -> None:
    html = f"<html><body><main>{_LONG_TEXT}</main></body></html>"
    headers = {"User-Agent": "leffic-tests"}

    with mock.patch.object(
        requests, "get", return_value=FakeResponse(html)
    ) as fake_get:
        _ = extract_link_main_content("http://test.com", headers)

    assert fake_get.call_args.kwargs["headers"] == headers


def test_skips_a_short_article_for_a_longer_content_div() -> None:
    html = (
        "<html><body><article>tiny</article>"
        f'<div class="content">{_LONG_TEXT}</div></body></html>'
    )

    with mock.patch.object(
        requests, "get", return_value=FakeResponse(html)
    ):
        assert extract_link_main_content("http://test.com") == _LONG_TEXT


def test_reads_the_main_element() -> None:
    html = f"<html><body><main>{_LONG_TEXT}</main></body></html>"

    with mock.patch.object(
        requests, "get", return_value=FakeResponse(html)
    ):
        assert extract_link_main_content("http://test.com") == _LONG_TEXT


def test_reads_a_content_section() -> None:
    html = (
        f'<html><body><section class="article">{_LONG_TEXT}'
        "</section></body></html>"
    )

    with mock.patch.object(
        requests, "get", return_value=FakeResponse(html)
    ):
        assert extract_link_main_content("http://test.com") == _LONG_TEXT


def test_ignores_a_div_without_a_content_class() -> None:
    html = (
        f'<html><body><div class="sidebar">{_LONG_TEXT}</div>'
        "</body></html>"
    )

    with mock.patch.object(
        requests, "get", return_value=FakeResponse(html)
    ):
        found = extract_link_main_content("http://test.com")

    assert found == _LONG_TEXT


def test_separates_blocks_with_newlines_and_strips_them() -> None:
    filler = "C" * 250
    html = (
        f"<html><body><article>  <p>{filler}</p>  <p>tail</p>  "
        "</article></body></html>"
    )

    with mock.patch.object(
        requests, "get", return_value=FakeResponse(html)
    ):
        found = extract_link_main_content("http://test.com")

    assert found == f"{filler}\ntail"
