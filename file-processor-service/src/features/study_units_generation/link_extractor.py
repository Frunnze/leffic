import re
from typing import cast
from urllib.parse import parse_qs, urlparse

import requests
from bs4 import BeautifulSoup, Tag
from youtube_transcript_api import (
    NoTranscriptFound,
    Transcript,
    TranscriptList,
    TranscriptsDisabled,
    YouTubeTranscriptApi,
)

_YOUTUBE_HOSTS = ("www.youtube.com", "youtube.com")
_SHORT_YOUTUBE_HOST = "youtu.be"
_DEFAULT_LANGUAGES = ("en",)
_MINIMUM_CONTENT_LENGTH = 200
_REQUEST_TIMEOUT_SECONDS = 10
_CONTENT_CLASS = re.compile(r"(content|main|article|body)", re.IGNORECASE)


def extract_video_id(url: str) -> str | None:
    parsed_url = urlparse(url)

    if parsed_url.hostname in _YOUTUBE_HOSTS:
        query = parse_qs(parsed_url.query)

        return query.get("v", [None])[0]

    if parsed_url.hostname == _SHORT_YOUTUBE_HOST:
        return parsed_url.path.lstrip("/")

    return None


def _joined_transcript(transcript: Transcript) -> str:
    return " ".join(entry.text for entry in transcript.fetch())


def _preferred_transcript(
    transcript_list: TranscriptList, preferred_langs: tuple[str, ...]
) -> Transcript | None:
    for finder in (
        transcript_list.find_manually_created_transcript,
        transcript_list.find_generated_transcript,
    ):
        for language in preferred_langs:
            try:
                return finder([language])
            except NoTranscriptFound:
                continue

    return None


def _any_transcript(transcript_list: TranscriptList) -> Transcript | None:
    # Fallback: any manually created transcript
    for transcript in transcript_list:
        if not transcript.is_generated:
            return transcript

    # Fallback: any auto-generated transcript
    for transcript in transcript_list:
        if transcript.is_generated:
            return transcript

    return None


def get_youtube_transcript_auto(
    link: str, preferred_langs: tuple[str, ...] = _DEFAULT_LANGUAGES
) -> str | None:
    video_id = extract_video_id(link)

    if not video_id:
        return None

    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
    except (TranscriptsDisabled, NoTranscriptFound):
        return None

    transcript = _preferred_transcript(
        transcript_list, preferred_langs
    ) or _any_transcript(transcript_list)

    if transcript is None:
        return None

    return _joined_transcript(transcript)


def _main_content_candidates(soup: BeautifulSoup) -> list[Tag]:
    # Try common containers for main content
    found = [
        soup.find("article"),
        soup.find("main"),
        soup.find("div", class_=_CONTENT_CLASS),
        soup.find("section", class_=_CONTENT_CLASS),
    ]

    return [candidate for candidate in found if isinstance(candidate, Tag)]


def _long_enough_text(candidate: Tag | None) -> str | None:
    if candidate is None:
        return None

    if len(candidate.get_text(strip=True)) <= _MINIMUM_CONTENT_LENGTH:
        return None

    return candidate.get_text(separator="\n", strip=True)


def extract_link_main_content(
    url: str, headers: dict[str, str] | None = None
) -> str | None:
    """
    Extracts the main readable content from a web page.

    Args:
        url (str): The URL of the web page.
        headers (dict, optional): Optional headers to include in the request.

    Returns:
        str: Extracted main text content of the page, or an error message.
    """
    try:
        response = requests.get(
            url, headers=headers, timeout=_REQUEST_TIMEOUT_SECONDS
        )
        response.raise_for_status()
    except requests.RequestException:
        return None

    soup = BeautifulSoup(
        cast("str", response.content), "html.parser"
    )

    for candidate in _main_content_candidates(soup):
        text = _long_enough_text(candidate)

        if text is not None:
            return text

    # Fallback: largest div by text length
    divs = [
        div
        for div in cast("list[object]", soup.find_all("div"))
        if isinstance(div, Tag)
    ]
    largest_div = max(divs, key=_text_length, default=None)

    return _long_enough_text(largest_div)


def _text_length(candidate: Tag) -> int:
    return len(candidate.get_text(strip=True))
