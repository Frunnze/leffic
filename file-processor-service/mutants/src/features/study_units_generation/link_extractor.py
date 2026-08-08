import re
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


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x_extract_video_id__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_extract_video_id__mutmut)
def extract_video_id(url: str) -> str | None:
    parsed_url = urlparse(url)

    if parsed_url.hostname in _YOUTUBE_HOSTS:
        query = parse_qs(parsed_url.query)

        return query.get("v", [None])[0]

    if parsed_url.hostname == _SHORT_YOUTUBE_HOST:
        return parsed_url.path.lstrip("/")

    return None


def x_extract_video_id__mutmut_orig(url: str) -> str | None:
    parsed_url = urlparse(url)

    if parsed_url.hostname in _YOUTUBE_HOSTS:
        query = parse_qs(parsed_url.query)

        return query.get("v", [None])[0]

    if parsed_url.hostname == _SHORT_YOUTUBE_HOST:
        return parsed_url.path.lstrip("/")

    return None


def x_extract_video_id__mutmut_1(url: str) -> str | None:
    parsed_url = None

    if parsed_url.hostname in _YOUTUBE_HOSTS:
        query = parse_qs(parsed_url.query)

        return query.get("v", [None])[0]

    if parsed_url.hostname == _SHORT_YOUTUBE_HOST:
        return parsed_url.path.lstrip("/")

    return None


def x_extract_video_id__mutmut_2(url: str) -> str | None:
    parsed_url = urlparse(None)

    if parsed_url.hostname in _YOUTUBE_HOSTS:
        query = parse_qs(parsed_url.query)

        return query.get("v", [None])[0]

    if parsed_url.hostname == _SHORT_YOUTUBE_HOST:
        return parsed_url.path.lstrip("/")

    return None


def x_extract_video_id__mutmut_3(url: str) -> str | None:
    parsed_url = urlparse(url)

    if parsed_url.hostname not in _YOUTUBE_HOSTS:
        query = parse_qs(parsed_url.query)

        return query.get("v", [None])[0]

    if parsed_url.hostname == _SHORT_YOUTUBE_HOST:
        return parsed_url.path.lstrip("/")

    return None


def x_extract_video_id__mutmut_4(url: str) -> str | None:
    parsed_url = urlparse(url)

    if parsed_url.hostname in _YOUTUBE_HOSTS:
        query = None

        return query.get("v", [None])[0]

    if parsed_url.hostname == _SHORT_YOUTUBE_HOST:
        return parsed_url.path.lstrip("/")

    return None


def x_extract_video_id__mutmut_5(url: str) -> str | None:
    parsed_url = urlparse(url)

    if parsed_url.hostname in _YOUTUBE_HOSTS:
        query = parse_qs(None)

        return query.get("v", [None])[0]

    if parsed_url.hostname == _SHORT_YOUTUBE_HOST:
        return parsed_url.path.lstrip("/")

    return None


def x_extract_video_id__mutmut_6(url: str) -> str | None:
    parsed_url = urlparse(url)

    if parsed_url.hostname in _YOUTUBE_HOSTS:
        query = parse_qs(parsed_url.query)

        return query.get(None, [None])[0]

    if parsed_url.hostname == _SHORT_YOUTUBE_HOST:
        return parsed_url.path.lstrip("/")

    return None


def x_extract_video_id__mutmut_7(url: str) -> str | None:
    parsed_url = urlparse(url)

    if parsed_url.hostname in _YOUTUBE_HOSTS:
        query = parse_qs(parsed_url.query)

        return query.get("v", None)[0]

    if parsed_url.hostname == _SHORT_YOUTUBE_HOST:
        return parsed_url.path.lstrip("/")

    return None


def x_extract_video_id__mutmut_8(url: str) -> str | None:
    parsed_url = urlparse(url)

    if parsed_url.hostname in _YOUTUBE_HOSTS:
        query = parse_qs(parsed_url.query)

        return query.get([None])[0]

    if parsed_url.hostname == _SHORT_YOUTUBE_HOST:
        return parsed_url.path.lstrip("/")

    return None


def x_extract_video_id__mutmut_9(url: str) -> str | None:
    parsed_url = urlparse(url)

    if parsed_url.hostname in _YOUTUBE_HOSTS:
        query = parse_qs(parsed_url.query)

        return query.get("v", )[0]

    if parsed_url.hostname == _SHORT_YOUTUBE_HOST:
        return parsed_url.path.lstrip("/")

    return None


def x_extract_video_id__mutmut_10(url: str) -> str | None:
    parsed_url = urlparse(url)

    if parsed_url.hostname in _YOUTUBE_HOSTS:
        query = parse_qs(parsed_url.query)

        return query.get("XXvXX", [None])[0]

    if parsed_url.hostname == _SHORT_YOUTUBE_HOST:
        return parsed_url.path.lstrip("/")

    return None


def x_extract_video_id__mutmut_11(url: str) -> str | None:
    parsed_url = urlparse(url)

    if parsed_url.hostname in _YOUTUBE_HOSTS:
        query = parse_qs(parsed_url.query)

        return query.get("V", [None])[0]

    if parsed_url.hostname == _SHORT_YOUTUBE_HOST:
        return parsed_url.path.lstrip("/")

    return None


def x_extract_video_id__mutmut_12(url: str) -> str | None:
    parsed_url = urlparse(url)

    if parsed_url.hostname in _YOUTUBE_HOSTS:
        query = parse_qs(parsed_url.query)

        return query.get("v", [None])[1]

    if parsed_url.hostname == _SHORT_YOUTUBE_HOST:
        return parsed_url.path.lstrip("/")

    return None


def x_extract_video_id__mutmut_13(url: str) -> str | None:
    parsed_url = urlparse(url)

    if parsed_url.hostname in _YOUTUBE_HOSTS:
        query = parse_qs(parsed_url.query)

        return query.get("v", [None])[0]

    if parsed_url.hostname != _SHORT_YOUTUBE_HOST:
        return parsed_url.path.lstrip("/")

    return None


def x_extract_video_id__mutmut_14(url: str) -> str | None:
    parsed_url = urlparse(url)

    if parsed_url.hostname in _YOUTUBE_HOSTS:
        query = parse_qs(parsed_url.query)

        return query.get("v", [None])[0]

    if parsed_url.hostname == _SHORT_YOUTUBE_HOST:
        return parsed_url.path.lstrip(None)

    return None


def x_extract_video_id__mutmut_15(url: str) -> str | None:
    parsed_url = urlparse(url)

    if parsed_url.hostname in _YOUTUBE_HOSTS:
        query = parse_qs(parsed_url.query)

        return query.get("v", [None])[0]

    if parsed_url.hostname == _SHORT_YOUTUBE_HOST:
        return parsed_url.path.rstrip("/")

    return None


def x_extract_video_id__mutmut_16(url: str) -> str | None:
    parsed_url = urlparse(url)

    if parsed_url.hostname in _YOUTUBE_HOSTS:
        query = parse_qs(parsed_url.query)

        return query.get("v", [None])[0]

    if parsed_url.hostname == _SHORT_YOUTUBE_HOST:
        return parsed_url.path.lstrip("XX/XX")

    return None

mutants_x_extract_video_id__mutmut['_mutmut_orig'] = x_extract_video_id__mutmut_orig # type: ignore # mutmut generated
mutants_x_extract_video_id__mutmut['x_extract_video_id__mutmut_1'] = x_extract_video_id__mutmut_1 # type: ignore # mutmut generated
mutants_x_extract_video_id__mutmut['x_extract_video_id__mutmut_2'] = x_extract_video_id__mutmut_2 # type: ignore # mutmut generated
mutants_x_extract_video_id__mutmut['x_extract_video_id__mutmut_3'] = x_extract_video_id__mutmut_3 # type: ignore # mutmut generated
mutants_x_extract_video_id__mutmut['x_extract_video_id__mutmut_4'] = x_extract_video_id__mutmut_4 # type: ignore # mutmut generated
mutants_x_extract_video_id__mutmut['x_extract_video_id__mutmut_5'] = x_extract_video_id__mutmut_5 # type: ignore # mutmut generated
mutants_x_extract_video_id__mutmut['x_extract_video_id__mutmut_6'] = x_extract_video_id__mutmut_6 # type: ignore # mutmut generated
mutants_x_extract_video_id__mutmut['x_extract_video_id__mutmut_7'] = x_extract_video_id__mutmut_7 # type: ignore # mutmut generated
mutants_x_extract_video_id__mutmut['x_extract_video_id__mutmut_8'] = x_extract_video_id__mutmut_8 # type: ignore # mutmut generated
mutants_x_extract_video_id__mutmut['x_extract_video_id__mutmut_9'] = x_extract_video_id__mutmut_9 # type: ignore # mutmut generated
mutants_x_extract_video_id__mutmut['x_extract_video_id__mutmut_10'] = x_extract_video_id__mutmut_10 # type: ignore # mutmut generated
mutants_x_extract_video_id__mutmut['x_extract_video_id__mutmut_11'] = x_extract_video_id__mutmut_11 # type: ignore # mutmut generated
mutants_x_extract_video_id__mutmut['x_extract_video_id__mutmut_12'] = x_extract_video_id__mutmut_12 # type: ignore # mutmut generated
mutants_x_extract_video_id__mutmut['x_extract_video_id__mutmut_13'] = x_extract_video_id__mutmut_13 # type: ignore # mutmut generated
mutants_x_extract_video_id__mutmut['x_extract_video_id__mutmut_14'] = x_extract_video_id__mutmut_14 # type: ignore # mutmut generated
mutants_x_extract_video_id__mutmut['x_extract_video_id__mutmut_15'] = x_extract_video_id__mutmut_15 # type: ignore # mutmut generated
mutants_x_extract_video_id__mutmut['x_extract_video_id__mutmut_16'] = x_extract_video_id__mutmut_16 # type: ignore # mutmut generated
mutants_x__joined_transcript__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__joined_transcript__mutmut)
def _joined_transcript(transcript: Transcript) -> str:
    return " ".join(entry.text for entry in transcript.fetch())


def x__joined_transcript__mutmut_orig(transcript: Transcript) -> str:
    return " ".join(entry.text for entry in transcript.fetch())


def x__joined_transcript__mutmut_1(transcript: Transcript) -> str:
    return " ".join(None)


def x__joined_transcript__mutmut_2(transcript: Transcript) -> str:
    return "XX XX".join(entry.text for entry in transcript.fetch())

mutants_x__joined_transcript__mutmut['_mutmut_orig'] = x__joined_transcript__mutmut_orig # type: ignore # mutmut generated
mutants_x__joined_transcript__mutmut['x__joined_transcript__mutmut_1'] = x__joined_transcript__mutmut_1 # type: ignore # mutmut generated
mutants_x__joined_transcript__mutmut['x__joined_transcript__mutmut_2'] = x__joined_transcript__mutmut_2 # type: ignore # mutmut generated
mutants_x__preferred_transcript__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__preferred_transcript__mutmut)
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


def x__preferred_transcript__mutmut_orig(
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


def x__preferred_transcript__mutmut_1(
    transcript_list: TranscriptList, preferred_langs: tuple[str, ...]
) -> Transcript | None:
    for finder in (
        transcript_list.find_manually_created_transcript,
        transcript_list.find_generated_transcript,
    ):
        for language in preferred_langs:
            try:
                return finder(None)
            except NoTranscriptFound:
                continue

    return None


def x__preferred_transcript__mutmut_2(
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
                break

    return None

mutants_x__preferred_transcript__mutmut['_mutmut_orig'] = x__preferred_transcript__mutmut_orig # type: ignore # mutmut generated
mutants_x__preferred_transcript__mutmut['x__preferred_transcript__mutmut_1'] = x__preferred_transcript__mutmut_1 # type: ignore # mutmut generated
mutants_x__preferred_transcript__mutmut['x__preferred_transcript__mutmut_2'] = x__preferred_transcript__mutmut_2 # type: ignore # mutmut generated
mutants_x__any_transcript__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__any_transcript__mutmut)
def _any_transcript(transcript_list: TranscriptList) -> Transcript | None:
    # Fallback: any manually created transcript
    for transcript in transcript_list:
        if not transcript.is_generated:
            return transcript

    # Fallback: any auto-generated transcript
    return next(iter(transcript_list), None)


def x__any_transcript__mutmut_orig(transcript_list: TranscriptList) -> Transcript | None:
    # Fallback: any manually created transcript
    for transcript in transcript_list:
        if not transcript.is_generated:
            return transcript

    # Fallback: any auto-generated transcript
    return next(iter(transcript_list), None)


def x__any_transcript__mutmut_1(transcript_list: TranscriptList) -> Transcript | None:
    # Fallback: any manually created transcript
    for transcript in transcript_list:
        if transcript.is_generated:
            return transcript

    # Fallback: any auto-generated transcript
    return next(iter(transcript_list), None)


def x__any_transcript__mutmut_2(transcript_list: TranscriptList) -> Transcript | None:
    # Fallback: any manually created transcript
    for transcript in transcript_list:
        if not transcript.is_generated:
            return transcript

    # Fallback: any auto-generated transcript
    return next(None, None)


def x__any_transcript__mutmut_3(transcript_list: TranscriptList) -> Transcript | None:
    # Fallback: any manually created transcript
    for transcript in transcript_list:
        if not transcript.is_generated:
            return transcript

    # Fallback: any auto-generated transcript
    return next(None)


def x__any_transcript__mutmut_4(transcript_list: TranscriptList) -> Transcript | None:
    # Fallback: any manually created transcript
    for transcript in transcript_list:
        if not transcript.is_generated:
            return transcript

    # Fallback: any auto-generated transcript
    return next(iter(transcript_list), )


def x__any_transcript__mutmut_5(transcript_list: TranscriptList) -> Transcript | None:
    # Fallback: any manually created transcript
    for transcript in transcript_list:
        if not transcript.is_generated:
            return transcript

    # Fallback: any auto-generated transcript
    return next(iter(None), None)

mutants_x__any_transcript__mutmut['_mutmut_orig'] = x__any_transcript__mutmut_orig # type: ignore # mutmut generated
mutants_x__any_transcript__mutmut['x__any_transcript__mutmut_1'] = x__any_transcript__mutmut_1 # type: ignore # mutmut generated
mutants_x__any_transcript__mutmut['x__any_transcript__mutmut_2'] = x__any_transcript__mutmut_2 # type: ignore # mutmut generated
mutants_x__any_transcript__mutmut['x__any_transcript__mutmut_3'] = x__any_transcript__mutmut_3 # type: ignore # mutmut generated
mutants_x__any_transcript__mutmut['x__any_transcript__mutmut_4'] = x__any_transcript__mutmut_4 # type: ignore # mutmut generated
mutants_x__any_transcript__mutmut['x__any_transcript__mutmut_5'] = x__any_transcript__mutmut_5 # type: ignore # mutmut generated
mutants_x_get_youtube_transcript_auto__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_get_youtube_transcript_auto__mutmut)
def get_youtube_transcript_auto(
    link: str, preferred_langs: tuple[str, ...] = _DEFAULT_LANGUAGES
) -> str | None:
    video_id = extract_video_id(link)

    if not video_id:
        return None

    try:
        transcript_list = YouTubeTranscriptApi().list(video_id)
    except (TranscriptsDisabled, NoTranscriptFound):
        return None

    transcript = _preferred_transcript(
        transcript_list, preferred_langs
    ) or _any_transcript(transcript_list)

    if transcript is None:
        return None

    return _joined_transcript(transcript)


def x_get_youtube_transcript_auto__mutmut_orig(
    link: str, preferred_langs: tuple[str, ...] = _DEFAULT_LANGUAGES
) -> str | None:
    video_id = extract_video_id(link)

    if not video_id:
        return None

    try:
        transcript_list = YouTubeTranscriptApi().list(video_id)
    except (TranscriptsDisabled, NoTranscriptFound):
        return None

    transcript = _preferred_transcript(
        transcript_list, preferred_langs
    ) or _any_transcript(transcript_list)

    if transcript is None:
        return None

    return _joined_transcript(transcript)


def x_get_youtube_transcript_auto__mutmut_1(
    link: str, preferred_langs: tuple[str, ...] = _DEFAULT_LANGUAGES
) -> str | None:
    video_id = None

    if not video_id:
        return None

    try:
        transcript_list = YouTubeTranscriptApi().list(video_id)
    except (TranscriptsDisabled, NoTranscriptFound):
        return None

    transcript = _preferred_transcript(
        transcript_list, preferred_langs
    ) or _any_transcript(transcript_list)

    if transcript is None:
        return None

    return _joined_transcript(transcript)


def x_get_youtube_transcript_auto__mutmut_2(
    link: str, preferred_langs: tuple[str, ...] = _DEFAULT_LANGUAGES
) -> str | None:
    video_id = extract_video_id(None)

    if not video_id:
        return None

    try:
        transcript_list = YouTubeTranscriptApi().list(video_id)
    except (TranscriptsDisabled, NoTranscriptFound):
        return None

    transcript = _preferred_transcript(
        transcript_list, preferred_langs
    ) or _any_transcript(transcript_list)

    if transcript is None:
        return None

    return _joined_transcript(transcript)


def x_get_youtube_transcript_auto__mutmut_3(
    link: str, preferred_langs: tuple[str, ...] = _DEFAULT_LANGUAGES
) -> str | None:
    video_id = extract_video_id(link)

    if video_id:
        return None

    try:
        transcript_list = YouTubeTranscriptApi().list(video_id)
    except (TranscriptsDisabled, NoTranscriptFound):
        return None

    transcript = _preferred_transcript(
        transcript_list, preferred_langs
    ) or _any_transcript(transcript_list)

    if transcript is None:
        return None

    return _joined_transcript(transcript)


def x_get_youtube_transcript_auto__mutmut_4(
    link: str, preferred_langs: tuple[str, ...] = _DEFAULT_LANGUAGES
) -> str | None:
    video_id = extract_video_id(link)

    if not video_id:
        return None

    try:
        transcript_list = None
    except (TranscriptsDisabled, NoTranscriptFound):
        return None

    transcript = _preferred_transcript(
        transcript_list, preferred_langs
    ) or _any_transcript(transcript_list)

    if transcript is None:
        return None

    return _joined_transcript(transcript)


def x_get_youtube_transcript_auto__mutmut_5(
    link: str, preferred_langs: tuple[str, ...] = _DEFAULT_LANGUAGES
) -> str | None:
    video_id = extract_video_id(link)

    if not video_id:
        return None

    try:
        transcript_list = YouTubeTranscriptApi().list(None)
    except (TranscriptsDisabled, NoTranscriptFound):
        return None

    transcript = _preferred_transcript(
        transcript_list, preferred_langs
    ) or _any_transcript(transcript_list)

    if transcript is None:
        return None

    return _joined_transcript(transcript)


def x_get_youtube_transcript_auto__mutmut_6(
    link: str, preferred_langs: tuple[str, ...] = _DEFAULT_LANGUAGES
) -> str | None:
    video_id = extract_video_id(link)

    if not video_id:
        return None

    try:
        transcript_list = YouTubeTranscriptApi().list(video_id)
    except (TranscriptsDisabled, NoTranscriptFound):
        return None

    transcript = None

    if transcript is None:
        return None

    return _joined_transcript(transcript)


def x_get_youtube_transcript_auto__mutmut_7(
    link: str, preferred_langs: tuple[str, ...] = _DEFAULT_LANGUAGES
) -> str | None:
    video_id = extract_video_id(link)

    if not video_id:
        return None

    try:
        transcript_list = YouTubeTranscriptApi().list(video_id)
    except (TranscriptsDisabled, NoTranscriptFound):
        return None

    transcript = _preferred_transcript(
        transcript_list, preferred_langs
    ) and _any_transcript(transcript_list)

    if transcript is None:
        return None

    return _joined_transcript(transcript)


def x_get_youtube_transcript_auto__mutmut_8(
    link: str, preferred_langs: tuple[str, ...] = _DEFAULT_LANGUAGES
) -> str | None:
    video_id = extract_video_id(link)

    if not video_id:
        return None

    try:
        transcript_list = YouTubeTranscriptApi().list(video_id)
    except (TranscriptsDisabled, NoTranscriptFound):
        return None

    transcript = _preferred_transcript(
        None, preferred_langs
    ) or _any_transcript(transcript_list)

    if transcript is None:
        return None

    return _joined_transcript(transcript)


def x_get_youtube_transcript_auto__mutmut_9(
    link: str, preferred_langs: tuple[str, ...] = _DEFAULT_LANGUAGES
) -> str | None:
    video_id = extract_video_id(link)

    if not video_id:
        return None

    try:
        transcript_list = YouTubeTranscriptApi().list(video_id)
    except (TranscriptsDisabled, NoTranscriptFound):
        return None

    transcript = _preferred_transcript(
        transcript_list, None
    ) or _any_transcript(transcript_list)

    if transcript is None:
        return None

    return _joined_transcript(transcript)


def x_get_youtube_transcript_auto__mutmut_10(
    link: str, preferred_langs: tuple[str, ...] = _DEFAULT_LANGUAGES
) -> str | None:
    video_id = extract_video_id(link)

    if not video_id:
        return None

    try:
        transcript_list = YouTubeTranscriptApi().list(video_id)
    except (TranscriptsDisabled, NoTranscriptFound):
        return None

    transcript = _preferred_transcript(
        preferred_langs
    ) or _any_transcript(transcript_list)

    if transcript is None:
        return None

    return _joined_transcript(transcript)


def x_get_youtube_transcript_auto__mutmut_11(
    link: str, preferred_langs: tuple[str, ...] = _DEFAULT_LANGUAGES
) -> str | None:
    video_id = extract_video_id(link)

    if not video_id:
        return None

    try:
        transcript_list = YouTubeTranscriptApi().list(video_id)
    except (TranscriptsDisabled, NoTranscriptFound):
        return None

    transcript = _preferred_transcript(
        transcript_list, ) or _any_transcript(transcript_list)

    if transcript is None:
        return None

    return _joined_transcript(transcript)


def x_get_youtube_transcript_auto__mutmut_12(
    link: str, preferred_langs: tuple[str, ...] = _DEFAULT_LANGUAGES
) -> str | None:
    video_id = extract_video_id(link)

    if not video_id:
        return None

    try:
        transcript_list = YouTubeTranscriptApi().list(video_id)
    except (TranscriptsDisabled, NoTranscriptFound):
        return None

    transcript = _preferred_transcript(
        transcript_list, preferred_langs
    ) or _any_transcript(None)

    if transcript is None:
        return None

    return _joined_transcript(transcript)


def x_get_youtube_transcript_auto__mutmut_13(
    link: str, preferred_langs: tuple[str, ...] = _DEFAULT_LANGUAGES
) -> str | None:
    video_id = extract_video_id(link)

    if not video_id:
        return None

    try:
        transcript_list = YouTubeTranscriptApi().list(video_id)
    except (TranscriptsDisabled, NoTranscriptFound):
        return None

    transcript = _preferred_transcript(
        transcript_list, preferred_langs
    ) or _any_transcript(transcript_list)

    if transcript is not None:
        return None

    return _joined_transcript(transcript)


def x_get_youtube_transcript_auto__mutmut_14(
    link: str, preferred_langs: tuple[str, ...] = _DEFAULT_LANGUAGES
) -> str | None:
    video_id = extract_video_id(link)

    if not video_id:
        return None

    try:
        transcript_list = YouTubeTranscriptApi().list(video_id)
    except (TranscriptsDisabled, NoTranscriptFound):
        return None

    transcript = _preferred_transcript(
        transcript_list, preferred_langs
    ) or _any_transcript(transcript_list)

    if transcript is None:
        return None

    return _joined_transcript(None)

mutants_x_get_youtube_transcript_auto__mutmut['_mutmut_orig'] = x_get_youtube_transcript_auto__mutmut_orig # type: ignore # mutmut generated
mutants_x_get_youtube_transcript_auto__mutmut['x_get_youtube_transcript_auto__mutmut_1'] = x_get_youtube_transcript_auto__mutmut_1 # type: ignore # mutmut generated
mutants_x_get_youtube_transcript_auto__mutmut['x_get_youtube_transcript_auto__mutmut_2'] = x_get_youtube_transcript_auto__mutmut_2 # type: ignore # mutmut generated
mutants_x_get_youtube_transcript_auto__mutmut['x_get_youtube_transcript_auto__mutmut_3'] = x_get_youtube_transcript_auto__mutmut_3 # type: ignore # mutmut generated
mutants_x_get_youtube_transcript_auto__mutmut['x_get_youtube_transcript_auto__mutmut_4'] = x_get_youtube_transcript_auto__mutmut_4 # type: ignore # mutmut generated
mutants_x_get_youtube_transcript_auto__mutmut['x_get_youtube_transcript_auto__mutmut_5'] = x_get_youtube_transcript_auto__mutmut_5 # type: ignore # mutmut generated
mutants_x_get_youtube_transcript_auto__mutmut['x_get_youtube_transcript_auto__mutmut_6'] = x_get_youtube_transcript_auto__mutmut_6 # type: ignore # mutmut generated
mutants_x_get_youtube_transcript_auto__mutmut['x_get_youtube_transcript_auto__mutmut_7'] = x_get_youtube_transcript_auto__mutmut_7 # type: ignore # mutmut generated
mutants_x_get_youtube_transcript_auto__mutmut['x_get_youtube_transcript_auto__mutmut_8'] = x_get_youtube_transcript_auto__mutmut_8 # type: ignore # mutmut generated
mutants_x_get_youtube_transcript_auto__mutmut['x_get_youtube_transcript_auto__mutmut_9'] = x_get_youtube_transcript_auto__mutmut_9 # type: ignore # mutmut generated
mutants_x_get_youtube_transcript_auto__mutmut['x_get_youtube_transcript_auto__mutmut_10'] = x_get_youtube_transcript_auto__mutmut_10 # type: ignore # mutmut generated
mutants_x_get_youtube_transcript_auto__mutmut['x_get_youtube_transcript_auto__mutmut_11'] = x_get_youtube_transcript_auto__mutmut_11 # type: ignore # mutmut generated
mutants_x_get_youtube_transcript_auto__mutmut['x_get_youtube_transcript_auto__mutmut_12'] = x_get_youtube_transcript_auto__mutmut_12 # type: ignore # mutmut generated
mutants_x_get_youtube_transcript_auto__mutmut['x_get_youtube_transcript_auto__mutmut_13'] = x_get_youtube_transcript_auto__mutmut_13 # type: ignore # mutmut generated
mutants_x_get_youtube_transcript_auto__mutmut['x_get_youtube_transcript_auto__mutmut_14'] = x_get_youtube_transcript_auto__mutmut_14 # type: ignore # mutmut generated
mutants_x__main_content_candidates__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__main_content_candidates__mutmut)
def _main_content_candidates(soup: BeautifulSoup) -> list[Tag]:
    # Try common containers for main content
    found = [
        soup.find("article"),
        soup.find("main"),
        soup.find("div", class_=_CONTENT_CLASS),
        soup.find("section", class_=_CONTENT_CLASS),
    ]

    return [candidate for candidate in found if isinstance(candidate, Tag)]


def x__main_content_candidates__mutmut_orig(soup: BeautifulSoup) -> list[Tag]:
    # Try common containers for main content
    found = [
        soup.find("article"),
        soup.find("main"),
        soup.find("div", class_=_CONTENT_CLASS),
        soup.find("section", class_=_CONTENT_CLASS),
    ]

    return [candidate for candidate in found if isinstance(candidate, Tag)]


def x__main_content_candidates__mutmut_1(soup: BeautifulSoup) -> list[Tag]:
    # Try common containers for main content
    found = None

    return [candidate for candidate in found if isinstance(candidate, Tag)]


def x__main_content_candidates__mutmut_2(soup: BeautifulSoup) -> list[Tag]:
    # Try common containers for main content
    found = [
        soup.find(None),
        soup.find("main"),
        soup.find("div", class_=_CONTENT_CLASS),
        soup.find("section", class_=_CONTENT_CLASS),
    ]

    return [candidate for candidate in found if isinstance(candidate, Tag)]


def x__main_content_candidates__mutmut_3(soup: BeautifulSoup) -> list[Tag]:
    # Try common containers for main content
    found = [
        soup.rfind("article"),
        soup.find("main"),
        soup.find("div", class_=_CONTENT_CLASS),
        soup.find("section", class_=_CONTENT_CLASS),
    ]

    return [candidate for candidate in found if isinstance(candidate, Tag)]


def x__main_content_candidates__mutmut_4(soup: BeautifulSoup) -> list[Tag]:
    # Try common containers for main content
    found = [
        soup.find("XXarticleXX"),
        soup.find("main"),
        soup.find("div", class_=_CONTENT_CLASS),
        soup.find("section", class_=_CONTENT_CLASS),
    ]

    return [candidate for candidate in found if isinstance(candidate, Tag)]


def x__main_content_candidates__mutmut_5(soup: BeautifulSoup) -> list[Tag]:
    # Try common containers for main content
    found = [
        soup.find("ARTICLE"),
        soup.find("main"),
        soup.find("div", class_=_CONTENT_CLASS),
        soup.find("section", class_=_CONTENT_CLASS),
    ]

    return [candidate for candidate in found if isinstance(candidate, Tag)]


def x__main_content_candidates__mutmut_6(soup: BeautifulSoup) -> list[Tag]:
    # Try common containers for main content
    found = [
        soup.find("article"),
        soup.find(None),
        soup.find("div", class_=_CONTENT_CLASS),
        soup.find("section", class_=_CONTENT_CLASS),
    ]

    return [candidate for candidate in found if isinstance(candidate, Tag)]


def x__main_content_candidates__mutmut_7(soup: BeautifulSoup) -> list[Tag]:
    # Try common containers for main content
    found = [
        soup.find("article"),
        soup.rfind("main"),
        soup.find("div", class_=_CONTENT_CLASS),
        soup.find("section", class_=_CONTENT_CLASS),
    ]

    return [candidate for candidate in found if isinstance(candidate, Tag)]


def x__main_content_candidates__mutmut_8(soup: BeautifulSoup) -> list[Tag]:
    # Try common containers for main content
    found = [
        soup.find("article"),
        soup.find("XXmainXX"),
        soup.find("div", class_=_CONTENT_CLASS),
        soup.find("section", class_=_CONTENT_CLASS),
    ]

    return [candidate for candidate in found if isinstance(candidate, Tag)]


def x__main_content_candidates__mutmut_9(soup: BeautifulSoup) -> list[Tag]:
    # Try common containers for main content
    found = [
        soup.find("article"),
        soup.find("MAIN"),
        soup.find("div", class_=_CONTENT_CLASS),
        soup.find("section", class_=_CONTENT_CLASS),
    ]

    return [candidate for candidate in found if isinstance(candidate, Tag)]


def x__main_content_candidates__mutmut_10(soup: BeautifulSoup) -> list[Tag]:
    # Try common containers for main content
    found = [
        soup.find("article"),
        soup.find("main"),
        soup.find(None, class_=_CONTENT_CLASS),
        soup.find("section", class_=_CONTENT_CLASS),
    ]

    return [candidate for candidate in found if isinstance(candidate, Tag)]


def x__main_content_candidates__mutmut_11(soup: BeautifulSoup) -> list[Tag]:
    # Try common containers for main content
    found = [
        soup.find("article"),
        soup.find("main"),
        soup.find("div", class_=None),
        soup.find("section", class_=_CONTENT_CLASS),
    ]

    return [candidate for candidate in found if isinstance(candidate, Tag)]


def x__main_content_candidates__mutmut_12(soup: BeautifulSoup) -> list[Tag]:
    # Try common containers for main content
    found = [
        soup.find("article"),
        soup.find("main"),
        soup.find(class_=_CONTENT_CLASS),
        soup.find("section", class_=_CONTENT_CLASS),
    ]

    return [candidate for candidate in found if isinstance(candidate, Tag)]


def x__main_content_candidates__mutmut_13(soup: BeautifulSoup) -> list[Tag]:
    # Try common containers for main content
    found = [
        soup.find("article"),
        soup.find("main"),
        soup.find("div", ),
        soup.find("section", class_=_CONTENT_CLASS),
    ]

    return [candidate for candidate in found if isinstance(candidate, Tag)]


def x__main_content_candidates__mutmut_14(soup: BeautifulSoup) -> list[Tag]:
    # Try common containers for main content
    found = [
        soup.find("article"),
        soup.find("main"),
        soup.rfind("div", class_=_CONTENT_CLASS),
        soup.find("section", class_=_CONTENT_CLASS),
    ]

    return [candidate for candidate in found if isinstance(candidate, Tag)]


def x__main_content_candidates__mutmut_15(soup: BeautifulSoup) -> list[Tag]:
    # Try common containers for main content
    found = [
        soup.find("article"),
        soup.find("main"),
        soup.find("XXdivXX", class_=_CONTENT_CLASS),
        soup.find("section", class_=_CONTENT_CLASS),
    ]

    return [candidate for candidate in found if isinstance(candidate, Tag)]


def x__main_content_candidates__mutmut_16(soup: BeautifulSoup) -> list[Tag]:
    # Try common containers for main content
    found = [
        soup.find("article"),
        soup.find("main"),
        soup.find("DIV", class_=_CONTENT_CLASS),
        soup.find("section", class_=_CONTENT_CLASS),
    ]

    return [candidate for candidate in found if isinstance(candidate, Tag)]


def x__main_content_candidates__mutmut_17(soup: BeautifulSoup) -> list[Tag]:
    # Try common containers for main content
    found = [
        soup.find("article"),
        soup.find("main"),
        soup.find("div", class_=_CONTENT_CLASS),
        soup.find(None, class_=_CONTENT_CLASS),
    ]

    return [candidate for candidate in found if isinstance(candidate, Tag)]


def x__main_content_candidates__mutmut_18(soup: BeautifulSoup) -> list[Tag]:
    # Try common containers for main content
    found = [
        soup.find("article"),
        soup.find("main"),
        soup.find("div", class_=_CONTENT_CLASS),
        soup.find("section", class_=None),
    ]

    return [candidate for candidate in found if isinstance(candidate, Tag)]


def x__main_content_candidates__mutmut_19(soup: BeautifulSoup) -> list[Tag]:
    # Try common containers for main content
    found = [
        soup.find("article"),
        soup.find("main"),
        soup.find("div", class_=_CONTENT_CLASS),
        soup.find(class_=_CONTENT_CLASS),
    ]

    return [candidate for candidate in found if isinstance(candidate, Tag)]


def x__main_content_candidates__mutmut_20(soup: BeautifulSoup) -> list[Tag]:
    # Try common containers for main content
    found = [
        soup.find("article"),
        soup.find("main"),
        soup.find("div", class_=_CONTENT_CLASS),
        soup.find("section", ),
    ]

    return [candidate for candidate in found if isinstance(candidate, Tag)]


def x__main_content_candidates__mutmut_21(soup: BeautifulSoup) -> list[Tag]:
    # Try common containers for main content
    found = [
        soup.find("article"),
        soup.find("main"),
        soup.find("div", class_=_CONTENT_CLASS),
        soup.rfind("section", class_=_CONTENT_CLASS),
    ]

    return [candidate for candidate in found if isinstance(candidate, Tag)]


def x__main_content_candidates__mutmut_22(soup: BeautifulSoup) -> list[Tag]:
    # Try common containers for main content
    found = [
        soup.find("article"),
        soup.find("main"),
        soup.find("div", class_=_CONTENT_CLASS),
        soup.find("XXsectionXX", class_=_CONTENT_CLASS),
    ]

    return [candidate for candidate in found if isinstance(candidate, Tag)]


def x__main_content_candidates__mutmut_23(soup: BeautifulSoup) -> list[Tag]:
    # Try common containers for main content
    found = [
        soup.find("article"),
        soup.find("main"),
        soup.find("div", class_=_CONTENT_CLASS),
        soup.find("SECTION", class_=_CONTENT_CLASS),
    ]

    return [candidate for candidate in found if isinstance(candidate, Tag)]

mutants_x__main_content_candidates__mutmut['_mutmut_orig'] = x__main_content_candidates__mutmut_orig # type: ignore # mutmut generated
mutants_x__main_content_candidates__mutmut['x__main_content_candidates__mutmut_1'] = x__main_content_candidates__mutmut_1 # type: ignore # mutmut generated
mutants_x__main_content_candidates__mutmut['x__main_content_candidates__mutmut_2'] = x__main_content_candidates__mutmut_2 # type: ignore # mutmut generated
mutants_x__main_content_candidates__mutmut['x__main_content_candidates__mutmut_3'] = x__main_content_candidates__mutmut_3 # type: ignore # mutmut generated
mutants_x__main_content_candidates__mutmut['x__main_content_candidates__mutmut_4'] = x__main_content_candidates__mutmut_4 # type: ignore # mutmut generated
mutants_x__main_content_candidates__mutmut['x__main_content_candidates__mutmut_5'] = x__main_content_candidates__mutmut_5 # type: ignore # mutmut generated
mutants_x__main_content_candidates__mutmut['x__main_content_candidates__mutmut_6'] = x__main_content_candidates__mutmut_6 # type: ignore # mutmut generated
mutants_x__main_content_candidates__mutmut['x__main_content_candidates__mutmut_7'] = x__main_content_candidates__mutmut_7 # type: ignore # mutmut generated
mutants_x__main_content_candidates__mutmut['x__main_content_candidates__mutmut_8'] = x__main_content_candidates__mutmut_8 # type: ignore # mutmut generated
mutants_x__main_content_candidates__mutmut['x__main_content_candidates__mutmut_9'] = x__main_content_candidates__mutmut_9 # type: ignore # mutmut generated
mutants_x__main_content_candidates__mutmut['x__main_content_candidates__mutmut_10'] = x__main_content_candidates__mutmut_10 # type: ignore # mutmut generated
mutants_x__main_content_candidates__mutmut['x__main_content_candidates__mutmut_11'] = x__main_content_candidates__mutmut_11 # type: ignore # mutmut generated
mutants_x__main_content_candidates__mutmut['x__main_content_candidates__mutmut_12'] = x__main_content_candidates__mutmut_12 # type: ignore # mutmut generated
mutants_x__main_content_candidates__mutmut['x__main_content_candidates__mutmut_13'] = x__main_content_candidates__mutmut_13 # type: ignore # mutmut generated
mutants_x__main_content_candidates__mutmut['x__main_content_candidates__mutmut_14'] = x__main_content_candidates__mutmut_14 # type: ignore # mutmut generated
mutants_x__main_content_candidates__mutmut['x__main_content_candidates__mutmut_15'] = x__main_content_candidates__mutmut_15 # type: ignore # mutmut generated
mutants_x__main_content_candidates__mutmut['x__main_content_candidates__mutmut_16'] = x__main_content_candidates__mutmut_16 # type: ignore # mutmut generated
mutants_x__main_content_candidates__mutmut['x__main_content_candidates__mutmut_17'] = x__main_content_candidates__mutmut_17 # type: ignore # mutmut generated
mutants_x__main_content_candidates__mutmut['x__main_content_candidates__mutmut_18'] = x__main_content_candidates__mutmut_18 # type: ignore # mutmut generated
mutants_x__main_content_candidates__mutmut['x__main_content_candidates__mutmut_19'] = x__main_content_candidates__mutmut_19 # type: ignore # mutmut generated
mutants_x__main_content_candidates__mutmut['x__main_content_candidates__mutmut_20'] = x__main_content_candidates__mutmut_20 # type: ignore # mutmut generated
mutants_x__main_content_candidates__mutmut['x__main_content_candidates__mutmut_21'] = x__main_content_candidates__mutmut_21 # type: ignore # mutmut generated
mutants_x__main_content_candidates__mutmut['x__main_content_candidates__mutmut_22'] = x__main_content_candidates__mutmut_22 # type: ignore # mutmut generated
mutants_x__main_content_candidates__mutmut['x__main_content_candidates__mutmut_23'] = x__main_content_candidates__mutmut_23 # type: ignore # mutmut generated
mutants_x__long_enough_text__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__long_enough_text__mutmut)
def _long_enough_text(candidate: Tag | None) -> str | None:
    if candidate is None:
        return None

    if len(candidate.get_text(strip=True)) <= _MINIMUM_CONTENT_LENGTH:
        return None

    return candidate.get_text(separator="\n", strip=True)


def x__long_enough_text__mutmut_orig(candidate: Tag | None) -> str | None:
    if candidate is None:
        return None

    if len(candidate.get_text(strip=True)) <= _MINIMUM_CONTENT_LENGTH:
        return None

    return candidate.get_text(separator="\n", strip=True)


def x__long_enough_text__mutmut_1(candidate: Tag | None) -> str | None:
    if candidate is not None:
        return None

    if len(candidate.get_text(strip=True)) <= _MINIMUM_CONTENT_LENGTH:
        return None

    return candidate.get_text(separator="\n", strip=True)


def x__long_enough_text__mutmut_2(candidate: Tag | None) -> str | None:
    if candidate is None:
        return None

    if len(candidate.get_text(strip=True)) < _MINIMUM_CONTENT_LENGTH:
        return None

    return candidate.get_text(separator="\n", strip=True)


def x__long_enough_text__mutmut_3(candidate: Tag | None) -> str | None:
    if candidate is None:
        return None

    if len(candidate.get_text(strip=True)) <= _MINIMUM_CONTENT_LENGTH:
        return None

    return candidate.get_text(separator=None, strip=True)


def x__long_enough_text__mutmut_4(candidate: Tag | None) -> str | None:
    if candidate is None:
        return None

    if len(candidate.get_text(strip=True)) <= _MINIMUM_CONTENT_LENGTH:
        return None

    return candidate.get_text(separator="\n", strip=None)


def x__long_enough_text__mutmut_5(candidate: Tag | None) -> str | None:
    if candidate is None:
        return None

    if len(candidate.get_text(strip=True)) <= _MINIMUM_CONTENT_LENGTH:
        return None

    return candidate.get_text(strip=True)


def x__long_enough_text__mutmut_6(candidate: Tag | None) -> str | None:
    if candidate is None:
        return None

    if len(candidate.get_text(strip=True)) <= _MINIMUM_CONTENT_LENGTH:
        return None

    return candidate.get_text(separator="\n", )


def x__long_enough_text__mutmut_7(candidate: Tag | None) -> str | None:
    if candidate is None:
        return None

    if len(candidate.get_text(strip=True)) <= _MINIMUM_CONTENT_LENGTH:
        return None

    return candidate.get_text(separator="XX\nXX", strip=True)


def x__long_enough_text__mutmut_8(candidate: Tag | None) -> str | None:
    if candidate is None:
        return None

    if len(candidate.get_text(strip=True)) <= _MINIMUM_CONTENT_LENGTH:
        return None

    return candidate.get_text(separator="\n", strip=False)

mutants_x__long_enough_text__mutmut['_mutmut_orig'] = x__long_enough_text__mutmut_orig # type: ignore # mutmut generated
mutants_x__long_enough_text__mutmut['x__long_enough_text__mutmut_1'] = x__long_enough_text__mutmut_1 # type: ignore # mutmut generated
mutants_x__long_enough_text__mutmut['x__long_enough_text__mutmut_2'] = x__long_enough_text__mutmut_2 # type: ignore # mutmut generated
mutants_x__long_enough_text__mutmut['x__long_enough_text__mutmut_3'] = x__long_enough_text__mutmut_3 # type: ignore # mutmut generated
mutants_x__long_enough_text__mutmut['x__long_enough_text__mutmut_4'] = x__long_enough_text__mutmut_4 # type: ignore # mutmut generated
mutants_x__long_enough_text__mutmut['x__long_enough_text__mutmut_5'] = x__long_enough_text__mutmut_5 # type: ignore # mutmut generated
mutants_x__long_enough_text__mutmut['x__long_enough_text__mutmut_6'] = x__long_enough_text__mutmut_6 # type: ignore # mutmut generated
mutants_x__long_enough_text__mutmut['x__long_enough_text__mutmut_7'] = x__long_enough_text__mutmut_7 # type: ignore # mutmut generated
mutants_x__long_enough_text__mutmut['x__long_enough_text__mutmut_8'] = x__long_enough_text__mutmut_8 # type: ignore # mutmut generated
mutants_x_extract_link_main_content__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_extract_link_main_content__mutmut)
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

    soup = BeautifulSoup(response.text, "html.parser")

    for candidate in _main_content_candidates(soup):
        text = _long_enough_text(candidate)

        if text is not None:
            return text

    # Fallback: largest div by text length
    divs = [
        div for div in _elements(soup, "div") if isinstance(div, Tag)
    ]
    largest_div = max(divs, key=_text_length, default=None)

    return _long_enough_text(largest_div)


def x_extract_link_main_content__mutmut_orig(
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

    soup = BeautifulSoup(response.text, "html.parser")

    for candidate in _main_content_candidates(soup):
        text = _long_enough_text(candidate)

        if text is not None:
            return text

    # Fallback: largest div by text length
    divs = [
        div for div in _elements(soup, "div") if isinstance(div, Tag)
    ]
    largest_div = max(divs, key=_text_length, default=None)

    return _long_enough_text(largest_div)


def x_extract_link_main_content__mutmut_1(
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
        response = None
        response.raise_for_status()
    except requests.RequestException:
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    for candidate in _main_content_candidates(soup):
        text = _long_enough_text(candidate)

        if text is not None:
            return text

    # Fallback: largest div by text length
    divs = [
        div for div in _elements(soup, "div") if isinstance(div, Tag)
    ]
    largest_div = max(divs, key=_text_length, default=None)

    return _long_enough_text(largest_div)


def x_extract_link_main_content__mutmut_2(
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
            None, headers=headers, timeout=_REQUEST_TIMEOUT_SECONDS
        )
        response.raise_for_status()
    except requests.RequestException:
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    for candidate in _main_content_candidates(soup):
        text = _long_enough_text(candidate)

        if text is not None:
            return text

    # Fallback: largest div by text length
    divs = [
        div for div in _elements(soup, "div") if isinstance(div, Tag)
    ]
    largest_div = max(divs, key=_text_length, default=None)

    return _long_enough_text(largest_div)


def x_extract_link_main_content__mutmut_3(
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
            url, headers=None, timeout=_REQUEST_TIMEOUT_SECONDS
        )
        response.raise_for_status()
    except requests.RequestException:
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    for candidate in _main_content_candidates(soup):
        text = _long_enough_text(candidate)

        if text is not None:
            return text

    # Fallback: largest div by text length
    divs = [
        div for div in _elements(soup, "div") if isinstance(div, Tag)
    ]
    largest_div = max(divs, key=_text_length, default=None)

    return _long_enough_text(largest_div)


def x_extract_link_main_content__mutmut_4(
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
            url, headers=headers, timeout=None
        )
        response.raise_for_status()
    except requests.RequestException:
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    for candidate in _main_content_candidates(soup):
        text = _long_enough_text(candidate)

        if text is not None:
            return text

    # Fallback: largest div by text length
    divs = [
        div for div in _elements(soup, "div") if isinstance(div, Tag)
    ]
    largest_div = max(divs, key=_text_length, default=None)

    return _long_enough_text(largest_div)


def x_extract_link_main_content__mutmut_5(
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
            headers=headers, timeout=_REQUEST_TIMEOUT_SECONDS
        )
        response.raise_for_status()
    except requests.RequestException:
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    for candidate in _main_content_candidates(soup):
        text = _long_enough_text(candidate)

        if text is not None:
            return text

    # Fallback: largest div by text length
    divs = [
        div for div in _elements(soup, "div") if isinstance(div, Tag)
    ]
    largest_div = max(divs, key=_text_length, default=None)

    return _long_enough_text(largest_div)


def x_extract_link_main_content__mutmut_6(
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
            url, timeout=_REQUEST_TIMEOUT_SECONDS
        )
        response.raise_for_status()
    except requests.RequestException:
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    for candidate in _main_content_candidates(soup):
        text = _long_enough_text(candidate)

        if text is not None:
            return text

    # Fallback: largest div by text length
    divs = [
        div for div in _elements(soup, "div") if isinstance(div, Tag)
    ]
    largest_div = max(divs, key=_text_length, default=None)

    return _long_enough_text(largest_div)


def x_extract_link_main_content__mutmut_7(
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
            url, headers=headers, )
        response.raise_for_status()
    except requests.RequestException:
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    for candidate in _main_content_candidates(soup):
        text = _long_enough_text(candidate)

        if text is not None:
            return text

    # Fallback: largest div by text length
    divs = [
        div for div in _elements(soup, "div") if isinstance(div, Tag)
    ]
    largest_div = max(divs, key=_text_length, default=None)

    return _long_enough_text(largest_div)


def x_extract_link_main_content__mutmut_8(
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

    soup = None

    for candidate in _main_content_candidates(soup):
        text = _long_enough_text(candidate)

        if text is not None:
            return text

    # Fallback: largest div by text length
    divs = [
        div for div in _elements(soup, "div") if isinstance(div, Tag)
    ]
    largest_div = max(divs, key=_text_length, default=None)

    return _long_enough_text(largest_div)


def x_extract_link_main_content__mutmut_9(
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

    soup = BeautifulSoup(None, "html.parser")

    for candidate in _main_content_candidates(soup):
        text = _long_enough_text(candidate)

        if text is not None:
            return text

    # Fallback: largest div by text length
    divs = [
        div for div in _elements(soup, "div") if isinstance(div, Tag)
    ]
    largest_div = max(divs, key=_text_length, default=None)

    return _long_enough_text(largest_div)


def x_extract_link_main_content__mutmut_10(
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

    soup = BeautifulSoup(response.text, None)

    for candidate in _main_content_candidates(soup):
        text = _long_enough_text(candidate)

        if text is not None:
            return text

    # Fallback: largest div by text length
    divs = [
        div for div in _elements(soup, "div") if isinstance(div, Tag)
    ]
    largest_div = max(divs, key=_text_length, default=None)

    return _long_enough_text(largest_div)


def x_extract_link_main_content__mutmut_11(
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

    soup = BeautifulSoup("html.parser")

    for candidate in _main_content_candidates(soup):
        text = _long_enough_text(candidate)

        if text is not None:
            return text

    # Fallback: largest div by text length
    divs = [
        div for div in _elements(soup, "div") if isinstance(div, Tag)
    ]
    largest_div = max(divs, key=_text_length, default=None)

    return _long_enough_text(largest_div)


def x_extract_link_main_content__mutmut_12(
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

    soup = BeautifulSoup(response.text, )

    for candidate in _main_content_candidates(soup):
        text = _long_enough_text(candidate)

        if text is not None:
            return text

    # Fallback: largest div by text length
    divs = [
        div for div in _elements(soup, "div") if isinstance(div, Tag)
    ]
    largest_div = max(divs, key=_text_length, default=None)

    return _long_enough_text(largest_div)


def x_extract_link_main_content__mutmut_13(
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

    soup = BeautifulSoup(response.text, "XXhtml.parserXX")

    for candidate in _main_content_candidates(soup):
        text = _long_enough_text(candidate)

        if text is not None:
            return text

    # Fallback: largest div by text length
    divs = [
        div for div in _elements(soup, "div") if isinstance(div, Tag)
    ]
    largest_div = max(divs, key=_text_length, default=None)

    return _long_enough_text(largest_div)


def x_extract_link_main_content__mutmut_14(
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

    soup = BeautifulSoup(response.text, "HTML.PARSER")

    for candidate in _main_content_candidates(soup):
        text = _long_enough_text(candidate)

        if text is not None:
            return text

    # Fallback: largest div by text length
    divs = [
        div for div in _elements(soup, "div") if isinstance(div, Tag)
    ]
    largest_div = max(divs, key=_text_length, default=None)

    return _long_enough_text(largest_div)


def x_extract_link_main_content__mutmut_15(
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

    soup = BeautifulSoup(response.text, "html.parser")

    for candidate in _main_content_candidates(None):
        text = _long_enough_text(candidate)

        if text is not None:
            return text

    # Fallback: largest div by text length
    divs = [
        div for div in _elements(soup, "div") if isinstance(div, Tag)
    ]
    largest_div = max(divs, key=_text_length, default=None)

    return _long_enough_text(largest_div)


def x_extract_link_main_content__mutmut_16(
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

    soup = BeautifulSoup(response.text, "html.parser")

    for candidate in _main_content_candidates(soup):
        text = None

        if text is not None:
            return text

    # Fallback: largest div by text length
    divs = [
        div for div in _elements(soup, "div") if isinstance(div, Tag)
    ]
    largest_div = max(divs, key=_text_length, default=None)

    return _long_enough_text(largest_div)


def x_extract_link_main_content__mutmut_17(
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

    soup = BeautifulSoup(response.text, "html.parser")

    for candidate in _main_content_candidates(soup):
        text = _long_enough_text(None)

        if text is not None:
            return text

    # Fallback: largest div by text length
    divs = [
        div for div in _elements(soup, "div") if isinstance(div, Tag)
    ]
    largest_div = max(divs, key=_text_length, default=None)

    return _long_enough_text(largest_div)


def x_extract_link_main_content__mutmut_18(
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

    soup = BeautifulSoup(response.text, "html.parser")

    for candidate in _main_content_candidates(soup):
        text = _long_enough_text(candidate)

        if text is None:
            return text

    # Fallback: largest div by text length
    divs = [
        div for div in _elements(soup, "div") if isinstance(div, Tag)
    ]
    largest_div = max(divs, key=_text_length, default=None)

    return _long_enough_text(largest_div)


def x_extract_link_main_content__mutmut_19(
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

    soup = BeautifulSoup(response.text, "html.parser")

    for candidate in _main_content_candidates(soup):
        text = _long_enough_text(candidate)

        if text is not None:
            return text

    # Fallback: largest div by text length
    divs = None
    largest_div = max(divs, key=_text_length, default=None)

    return _long_enough_text(largest_div)


def x_extract_link_main_content__mutmut_20(
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

    soup = BeautifulSoup(response.text, "html.parser")

    for candidate in _main_content_candidates(soup):
        text = _long_enough_text(candidate)

        if text is not None:
            return text

    # Fallback: largest div by text length
    divs = [
        div for div in _elements(None, "div") if isinstance(div, Tag)
    ]
    largest_div = max(divs, key=_text_length, default=None)

    return _long_enough_text(largest_div)


def x_extract_link_main_content__mutmut_21(
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

    soup = BeautifulSoup(response.text, "html.parser")

    for candidate in _main_content_candidates(soup):
        text = _long_enough_text(candidate)

        if text is not None:
            return text

    # Fallback: largest div by text length
    divs = [
        div for div in _elements(soup, None) if isinstance(div, Tag)
    ]
    largest_div = max(divs, key=_text_length, default=None)

    return _long_enough_text(largest_div)


def x_extract_link_main_content__mutmut_22(
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

    soup = BeautifulSoup(response.text, "html.parser")

    for candidate in _main_content_candidates(soup):
        text = _long_enough_text(candidate)

        if text is not None:
            return text

    # Fallback: largest div by text length
    divs = [
        div for div in _elements("div") if isinstance(div, Tag)
    ]
    largest_div = max(divs, key=_text_length, default=None)

    return _long_enough_text(largest_div)


def x_extract_link_main_content__mutmut_23(
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

    soup = BeautifulSoup(response.text, "html.parser")

    for candidate in _main_content_candidates(soup):
        text = _long_enough_text(candidate)

        if text is not None:
            return text

    # Fallback: largest div by text length
    divs = [
        div for div in _elements(soup, ) if isinstance(div, Tag)
    ]
    largest_div = max(divs, key=_text_length, default=None)

    return _long_enough_text(largest_div)


def x_extract_link_main_content__mutmut_24(
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

    soup = BeautifulSoup(response.text, "html.parser")

    for candidate in _main_content_candidates(soup):
        text = _long_enough_text(candidate)

        if text is not None:
            return text

    # Fallback: largest div by text length
    divs = [
        div for div in _elements(soup, "XXdivXX") if isinstance(div, Tag)
    ]
    largest_div = max(divs, key=_text_length, default=None)

    return _long_enough_text(largest_div)


def x_extract_link_main_content__mutmut_25(
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

    soup = BeautifulSoup(response.text, "html.parser")

    for candidate in _main_content_candidates(soup):
        text = _long_enough_text(candidate)

        if text is not None:
            return text

    # Fallback: largest div by text length
    divs = [
        div for div in _elements(soup, "DIV") if isinstance(div, Tag)
    ]
    largest_div = max(divs, key=_text_length, default=None)

    return _long_enough_text(largest_div)


def x_extract_link_main_content__mutmut_26(
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

    soup = BeautifulSoup(response.text, "html.parser")

    for candidate in _main_content_candidates(soup):
        text = _long_enough_text(candidate)

        if text is not None:
            return text

    # Fallback: largest div by text length
    divs = [
        div for div in _elements(soup, "div") if isinstance(div, Tag)
    ]
    largest_div = None

    return _long_enough_text(largest_div)


def x_extract_link_main_content__mutmut_27(
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

    soup = BeautifulSoup(response.text, "html.parser")

    for candidate in _main_content_candidates(soup):
        text = _long_enough_text(candidate)

        if text is not None:
            return text

    # Fallback: largest div by text length
    divs = [
        div for div in _elements(soup, "div") if isinstance(div, Tag)
    ]
    largest_div = max(None, key=_text_length, default=None)

    return _long_enough_text(largest_div)


def x_extract_link_main_content__mutmut_28(
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

    soup = BeautifulSoup(response.text, "html.parser")

    for candidate in _main_content_candidates(soup):
        text = _long_enough_text(candidate)

        if text is not None:
            return text

    # Fallback: largest div by text length
    divs = [
        div for div in _elements(soup, "div") if isinstance(div, Tag)
    ]
    largest_div = max(divs, key=None, default=None)

    return _long_enough_text(largest_div)


def x_extract_link_main_content__mutmut_29(
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

    soup = BeautifulSoup(response.text, "html.parser")

    for candidate in _main_content_candidates(soup):
        text = _long_enough_text(candidate)

        if text is not None:
            return text

    # Fallback: largest div by text length
    divs = [
        div for div in _elements(soup, "div") if isinstance(div, Tag)
    ]
    largest_div = max(key=_text_length, default=None)

    return _long_enough_text(largest_div)


def x_extract_link_main_content__mutmut_30(
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

    soup = BeautifulSoup(response.text, "html.parser")

    for candidate in _main_content_candidates(soup):
        text = _long_enough_text(candidate)

        if text is not None:
            return text

    # Fallback: largest div by text length
    divs = [
        div for div in _elements(soup, "div") if isinstance(div, Tag)
    ]
    largest_div = max(divs, default=None)

    return _long_enough_text(largest_div)


def x_extract_link_main_content__mutmut_31(
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

    soup = BeautifulSoup(response.text, "html.parser")

    for candidate in _main_content_candidates(soup):
        text = _long_enough_text(candidate)

        if text is not None:
            return text

    # Fallback: largest div by text length
    divs = [
        div for div in _elements(soup, "div") if isinstance(div, Tag)
    ]
    largest_div = max(divs, key=_text_length, )

    return _long_enough_text(largest_div)


def x_extract_link_main_content__mutmut_32(
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

    soup = BeautifulSoup(response.text, "html.parser")

    for candidate in _main_content_candidates(soup):
        text = _long_enough_text(candidate)

        if text is not None:
            return text

    # Fallback: largest div by text length
    divs = [
        div for div in _elements(soup, "div") if isinstance(div, Tag)
    ]
    largest_div = max(divs, key=_text_length, default=None)

    return _long_enough_text(None)

mutants_x_extract_link_main_content__mutmut['_mutmut_orig'] = x_extract_link_main_content__mutmut_orig # type: ignore # mutmut generated
mutants_x_extract_link_main_content__mutmut['x_extract_link_main_content__mutmut_1'] = x_extract_link_main_content__mutmut_1 # type: ignore # mutmut generated
mutants_x_extract_link_main_content__mutmut['x_extract_link_main_content__mutmut_2'] = x_extract_link_main_content__mutmut_2 # type: ignore # mutmut generated
mutants_x_extract_link_main_content__mutmut['x_extract_link_main_content__mutmut_3'] = x_extract_link_main_content__mutmut_3 # type: ignore # mutmut generated
mutants_x_extract_link_main_content__mutmut['x_extract_link_main_content__mutmut_4'] = x_extract_link_main_content__mutmut_4 # type: ignore # mutmut generated
mutants_x_extract_link_main_content__mutmut['x_extract_link_main_content__mutmut_5'] = x_extract_link_main_content__mutmut_5 # type: ignore # mutmut generated
mutants_x_extract_link_main_content__mutmut['x_extract_link_main_content__mutmut_6'] = x_extract_link_main_content__mutmut_6 # type: ignore # mutmut generated
mutants_x_extract_link_main_content__mutmut['x_extract_link_main_content__mutmut_7'] = x_extract_link_main_content__mutmut_7 # type: ignore # mutmut generated
mutants_x_extract_link_main_content__mutmut['x_extract_link_main_content__mutmut_8'] = x_extract_link_main_content__mutmut_8 # type: ignore # mutmut generated
mutants_x_extract_link_main_content__mutmut['x_extract_link_main_content__mutmut_9'] = x_extract_link_main_content__mutmut_9 # type: ignore # mutmut generated
mutants_x_extract_link_main_content__mutmut['x_extract_link_main_content__mutmut_10'] = x_extract_link_main_content__mutmut_10 # type: ignore # mutmut generated
mutants_x_extract_link_main_content__mutmut['x_extract_link_main_content__mutmut_11'] = x_extract_link_main_content__mutmut_11 # type: ignore # mutmut generated
mutants_x_extract_link_main_content__mutmut['x_extract_link_main_content__mutmut_12'] = x_extract_link_main_content__mutmut_12 # type: ignore # mutmut generated
mutants_x_extract_link_main_content__mutmut['x_extract_link_main_content__mutmut_13'] = x_extract_link_main_content__mutmut_13 # type: ignore # mutmut generated
mutants_x_extract_link_main_content__mutmut['x_extract_link_main_content__mutmut_14'] = x_extract_link_main_content__mutmut_14 # type: ignore # mutmut generated
mutants_x_extract_link_main_content__mutmut['x_extract_link_main_content__mutmut_15'] = x_extract_link_main_content__mutmut_15 # type: ignore # mutmut generated
mutants_x_extract_link_main_content__mutmut['x_extract_link_main_content__mutmut_16'] = x_extract_link_main_content__mutmut_16 # type: ignore # mutmut generated
mutants_x_extract_link_main_content__mutmut['x_extract_link_main_content__mutmut_17'] = x_extract_link_main_content__mutmut_17 # type: ignore # mutmut generated
mutants_x_extract_link_main_content__mutmut['x_extract_link_main_content__mutmut_18'] = x_extract_link_main_content__mutmut_18 # type: ignore # mutmut generated
mutants_x_extract_link_main_content__mutmut['x_extract_link_main_content__mutmut_19'] = x_extract_link_main_content__mutmut_19 # type: ignore # mutmut generated
mutants_x_extract_link_main_content__mutmut['x_extract_link_main_content__mutmut_20'] = x_extract_link_main_content__mutmut_20 # type: ignore # mutmut generated
mutants_x_extract_link_main_content__mutmut['x_extract_link_main_content__mutmut_21'] = x_extract_link_main_content__mutmut_21 # type: ignore # mutmut generated
mutants_x_extract_link_main_content__mutmut['x_extract_link_main_content__mutmut_22'] = x_extract_link_main_content__mutmut_22 # type: ignore # mutmut generated
mutants_x_extract_link_main_content__mutmut['x_extract_link_main_content__mutmut_23'] = x_extract_link_main_content__mutmut_23 # type: ignore # mutmut generated
mutants_x_extract_link_main_content__mutmut['x_extract_link_main_content__mutmut_24'] = x_extract_link_main_content__mutmut_24 # type: ignore # mutmut generated
mutants_x_extract_link_main_content__mutmut['x_extract_link_main_content__mutmut_25'] = x_extract_link_main_content__mutmut_25 # type: ignore # mutmut generated
mutants_x_extract_link_main_content__mutmut['x_extract_link_main_content__mutmut_26'] = x_extract_link_main_content__mutmut_26 # type: ignore # mutmut generated
mutants_x_extract_link_main_content__mutmut['x_extract_link_main_content__mutmut_27'] = x_extract_link_main_content__mutmut_27 # type: ignore # mutmut generated
mutants_x_extract_link_main_content__mutmut['x_extract_link_main_content__mutmut_28'] = x_extract_link_main_content__mutmut_28 # type: ignore # mutmut generated
mutants_x_extract_link_main_content__mutmut['x_extract_link_main_content__mutmut_29'] = x_extract_link_main_content__mutmut_29 # type: ignore # mutmut generated
mutants_x_extract_link_main_content__mutmut['x_extract_link_main_content__mutmut_30'] = x_extract_link_main_content__mutmut_30 # type: ignore # mutmut generated
mutants_x_extract_link_main_content__mutmut['x_extract_link_main_content__mutmut_31'] = x_extract_link_main_content__mutmut_31 # type: ignore # mutmut generated
mutants_x_extract_link_main_content__mutmut['x_extract_link_main_content__mutmut_32'] = x_extract_link_main_content__mutmut_32 # type: ignore # mutmut generated
mutants_x__elements__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x__elements__mutmut)
def _elements(soup: BeautifulSoup, name: str) -> list[object]:
    return list(soup.find_all(name))


def x__elements__mutmut_orig(soup: BeautifulSoup, name: str) -> list[object]:
    return list(soup.find_all(name))


def x__elements__mutmut_1(soup: BeautifulSoup, name: str) -> list[object]:
    return list(None)


def x__elements__mutmut_2(soup: BeautifulSoup, name: str) -> list[object]:
    return list(soup.find_all(None))

mutants_x__elements__mutmut['_mutmut_orig'] = x__elements__mutmut_orig # type: ignore # mutmut generated
mutants_x__elements__mutmut['x__elements__mutmut_1'] = x__elements__mutmut_1 # type: ignore # mutmut generated
mutants_x__elements__mutmut['x__elements__mutmut_2'] = x__elements__mutmut_2 # type: ignore # mutmut generated


def _text_length(candidate: Tag) -> int:
    return len(candidate.get_text(strip=True))
