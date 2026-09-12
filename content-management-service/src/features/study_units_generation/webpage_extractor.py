import re

import requests
from bs4 import BeautifulSoup, Tag

_MINIMUM_CONTENT_LENGTH = 200
_REQUEST_TIMEOUT_SECONDS = 10
_CONTENT_CLASS = re.compile(r"(content|main|article|body)", re.IGNORECASE)


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

    soup = BeautifulSoup(response.text, "html.parser")

    for candidate in _main_content_candidates(soup):
        text = _long_enough_text(candidate)

        if text is not None:
            return text

    # Fallback: largest div by text length
    divs = [div for div in _elements(soup, "div") if isinstance(div, Tag)]
    largest_div = max(divs, key=_text_length, default=None)

    return _long_enough_text(largest_div)


def _elements(soup: BeautifulSoup, name: str) -> list[object]:
    return list(soup.find_all(name))


def _text_length(candidate: Tag) -> int:
    return len(candidate.get_text(strip=True))
