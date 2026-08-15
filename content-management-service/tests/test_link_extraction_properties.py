from typing import cast
from unittest import mock

import requests
from bs4 import BeautifulSoup, Tag
from hypothesis import given, settings
from hypothesis import strategies as st
from youtube_transcript_api import Transcript, TranscriptList

from features.study_units_generation.link_extractor import (
    _any_transcript,
    _elements,
    _joined_transcript,
    _long_enough_text,
    _main_content_candidates,
    _preferred_transcript,
    _text_length,
    extract_link_main_content,
    extract_video_id,
    get_youtube_transcript_auto,
)
from tests.test_link_extractor import FakeTranscript, FakeTranscriptList

_MINIMUM_CONTENT_LENGTH = 200
_REQUESTS_GET = (
    "features.study_units_generation.link_extractor.requests.get"
)
_LANGUAGES = ("en",)
_VIDEO_IDS = st.text(
    alphabet=st.characters(min_codepoint=97, max_codepoint=122),
    min_size=5,
    max_size=11,
)
_SNIPPETS = st.lists(
    st.text(
        alphabet=st.characters(min_codepoint=97, max_codepoint=122),
        min_size=1,
        max_size=8,
    ),
    min_size=1,
    max_size=5,
)
_OTHER_HOSTS = st.sampled_from(
    ["https://example.com/watch?v=abc", "https://vimeo.com/12345", "notaurl"]
)


@settings(max_examples=50)
@given(_VIDEO_IDS)
def test_extract_video_id_property_reads_the_id_from_either_youtube_form(
    video_id: str,
) -> None:
    watch_url = f"https://www.youtube.com/watch?v={video_id}"
    short_url = f"https://youtu.be/{video_id}"

    assert extract_video_id(watch_url) == video_id
    assert extract_video_id(short_url) == video_id


@settings(max_examples=25)
@given(_OTHER_HOSTS)
def test_get_youtube_transcript_auto_property_ignores_other_hosts(
    url: str,
) -> None:
    assert get_youtube_transcript_auto(url) is None


@settings(max_examples=50)
@given(_SNIPPETS)
def test__joined_transcript_property_keeps_every_snippet_in_order(
    snippets: list[str],
) -> None:
    transcript = FakeTranscript(snippets[0], is_generated=False)
    transcript.extra_snippets = snippets[1:]

    assert _joined_transcript(cast("Transcript", cast("object", transcript))) == " ".join(
        snippets
    )


@settings(max_examples=25)
@given(st.booleans(), st.booleans())
def test__preferred_transcript_property_prefers_the_manual_one(
    has_manual: bool, has_generated: bool
) -> None:
    manual = FakeTranscript("manual", is_generated=False)
    generated = FakeTranscript("generated", is_generated=True)
    listing = FakeTranscriptList(
        [],
        manual_found=manual if has_manual else None,
        generated_found=generated if has_generated else None,
    )
    chosen = _preferred_transcript(
        cast("TranscriptList", cast("object", listing)), _LANGUAGES
    )

    if has_manual:
        assert chosen is manual
    elif has_generated:
        assert chosen is generated
    else:
        assert chosen is None


@settings(max_examples=25)
@given(st.lists(st.booleans(), max_size=4))
def test__any_transcript_property_prefers_anything_not_generated(
    generated_flags: list[bool],
) -> None:
    transcripts = [
        FakeTranscript(f"t{index}", is_generated=flag)
        for index, flag in enumerate(generated_flags)
    ]
    chosen = _any_transcript(
        cast("TranscriptList", cast("object", FakeTranscriptList(transcripts)))
    )

    if not transcripts:
        assert chosen is None
    elif any(not flag for flag in generated_flags):
        assert chosen is not None
        assert not chosen.is_generated
    else:
        assert chosen is transcripts[0]


@settings(max_examples=50)
@given(st.text(max_size=400))
def test__text_length_property_counts_the_stripped_text(text: str) -> None:
    soup = BeautifulSoup(f"<div>{text}</div>", "html.parser")
    div = cast("Tag", soup.find("div"))

    assert _text_length(div) == len(div.get_text(strip=True))


@settings(max_examples=50)
@given(st.integers(min_value=0, max_value=400))
def test__long_enough_text_property_refuses_anything_at_the_threshold(
    length: int,
) -> None:
    soup = BeautifulSoup(f"<div>{'a' * length}</div>", "html.parser")
    text = _long_enough_text(cast("Tag", soup.find("div")))

    assert (text is None) is (length <= _MINIMUM_CONTENT_LENGTH)


@settings(max_examples=25)
@given(st.integers(min_value=0, max_value=5))
def test__elements_property_finds_every_tag_of_that_name(
    count: int,
) -> None:
    soup = BeautifulSoup("<div>x</div>" * count, "html.parser")

    assert len(_elements(soup, "div")) == count


@settings(max_examples=25)
@given(st.lists(st.sampled_from(["article", "main"]), unique=True))
def test__main_content_candidates_property_returns_only_real_tags(
    tags: list[str],
) -> None:
    html = "".join(f"<{tag}>body</{tag}>" for tag in tags)
    candidates = _main_content_candidates(BeautifulSoup(html, "html.parser"))

    assert len(candidates) == len(tags)
    assert {candidate.name for candidate in candidates} == set(tags)


@settings(max_examples=25)
@given(st.sampled_from(["https://example.com", "https://example.org/a"]))
def test_extract_link_main_content_property_stays_quiet_when_it_cannot_fetch(
    url: str,
) -> None:
    with mock.patch(
        _REQUESTS_GET, side_effect=requests.RequestException("offline")
    ):
        assert extract_link_main_content(url) is None
