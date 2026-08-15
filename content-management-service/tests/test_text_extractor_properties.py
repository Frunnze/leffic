from unittest import mock

from hypothesis import given, settings
from hypothesis import strategies as st

from features.study_units_generation.text_extractor import (
    GeneralTextExtractor,
    TextExtractorFactory,
    text_extractor_factory,
)

_KNOWN_EXTENSIONS = st.sampled_from(["pdf", "docx", "txt", "png"])
_PADDING = st.sampled_from(["", " ", "\n", "  \t\n"])
_TEXTRACT_PROCESS = (
    "features.study_units_generation.text_extractor.textract.process"
)
_SPELLINGS = {
    "upper": str.upper,
    "lower": str.lower,
    "title": str.title,
}


@settings(max_examples=50)
@given(_KNOWN_EXTENSIONS, st.sampled_from(["upper", "lower", "title"]))
def test_get_text_extractor_property_ignores_the_spelling_of_the_case(
    extension: str, spelling: str
) -> None:
    spelled = _SPELLINGS[spelling](extension)
    found = text_extractor_factory.get_text_extractor(spelled)

    assert found is text_extractor_factory.get_text_extractor(extension)
    assert found is not None


@settings(max_examples=50)
@given(st.text(alphabet="abcdef", min_size=1, max_size=6))
def test_register_extractor_property_hands_back_what_was_registered(
    extension: str,
) -> None:
    factory = TextExtractorFactory()
    registered = GeneralTextExtractor()

    assert factory.get_text_extractor(extension) is None

    factory.register_extractor(extension.upper(), registered)

    assert factory.get_text_extractor(extension) is registered


@settings(max_examples=50)
@given(st.text(max_size=40), _PADDING, _PADDING)
def test_extract_text_property_returns_the_document_without_its_padding(
    body: str, before: str, after: str
) -> None:
    raw = f"{before}{body}{after}".encode()

    with mock.patch(_TEXTRACT_PROCESS, return_value=raw):
        extracted = GeneralTextExtractor().extract_text("a.pdf", "pdf")

    assert extracted == raw.decode("utf-8", errors="ignore").strip()


@settings(max_examples=25)
@given(st.integers(min_value=1, max_value=3))
def test___init___property_starts_a_factory_with_nothing_registered(
    count: int,
) -> None:
    factories = [TextExtractorFactory() for _ in range(count)]

    assert all(
        factory.get_text_extractor("pdf") is None for factory in factories
    )
