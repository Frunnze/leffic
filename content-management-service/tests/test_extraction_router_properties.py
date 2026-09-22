from hypothesis import given, settings
from hypothesis import strategies as st

from features.study_units_generation.extraction_router import (
    _extracted_text,
)
from features.study_units_generation.text_sources import StoredDocument

_TEXT = st.text(alphabet="abcdefg", min_size=1, max_size=12)
_SOURCES = st.sampled_from(["files", "link", "both", "neither"])
_LINK = "https://example.com"


class _FixedDocumentText:
    def __init__(self, text: str) -> None:
        self.text: str = text
        self.asked: list[list[StoredDocument]] = []

    def text_from_files(self, documents: list[StoredDocument]) -> str:
        self.asked.append(documents)

        return self.text


class _FixedLinkText:
    def __init__(self, text: str) -> None:
        self.text: str = text
        self.asked: list[str] = []

    def text_from_link(self, link: str) -> str:
        self.asked.append(link)

        return self.text


@settings(max_examples=50)
@given(_TEXT, _TEXT, _SOURCES)
def test__extracted_text_property_reads_whichever_source_was_given(
    document_body: str, link_body: str, source: str
) -> None:
    documents = (
        [StoredDocument(storage_name="f.pdf", extension="pdf")]
        if source in {"files", "both"}
        else []
    )
    link = _LINK if source in {"link", "both"} else None
    document_text = _FixedDocumentText(document_body)
    link_text = _FixedLinkText(link_body)

    extracted = _extracted_text(documents, link, document_text, link_text)

    expected = {
        "files": document_body,
        "link": link_body,
        "both": document_body,
        "neither": "",
    }

    assert extracted == expected[source]
    assert document_text.asked == ([documents] if documents else [])
    assert link_text.asked == ([_LINK] if source == "link" else [])
