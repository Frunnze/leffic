from unittest import mock

from features.study_units_generation import link_text
from features.study_units_generation.link_text import WebLinkText

_LINK_TEXT = WebLinkText()


def test_a_youtube_link_uses_the_transcript() -> None:
    link = "https://youtube.com/watch?v=x"

    with mock.patch.object(
        link_text, "get_youtube_transcript_auto", return_value="spoken"
    ) as transcript:
        assert _LINK_TEXT.text_from_link(link) == "spoken"

    assert transcript.call_args.args[0] == link


def test_a_youtube_link_without_a_transcript_reads_the_page() -> None:
    link = "https://youtube.com/watch?v=x"

    with (
        mock.patch.object(
            link_text, "get_youtube_transcript_auto", return_value=None
        ),
        mock.patch.object(
            link_text, "extract_link_main_content", return_value="page"
        ),
    ):
        assert _LINK_TEXT.text_from_link(link) == "page"


def test_a_plain_link_reads_the_page() -> None:
    link = "https://example.com/story"

    with mock.patch.object(
        link_text, "extract_link_main_content", return_value="article"
    ) as page:
        assert _LINK_TEXT.text_from_link(link) == "article"

    assert page.call_args.args[0] == link


def test_an_unreadable_link_yields_no_text() -> None:
    with mock.patch.object(
        link_text, "extract_link_main_content", return_value=None
    ):
        assert _LINK_TEXT.text_from_link("https://example.com") == ""
