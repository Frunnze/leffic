import tempfile
from pathlib import Path

import pytest
from fastapi import HTTPException
from hypothesis import given, settings
from hypothesis import strategies as st

from features.file_upload.file_uploader import _converted_to_pdf
from shared.pdf_conversion import ConversionError

_BAD_REQUEST = 400
_CONTENT = st.binary(min_size=1, max_size=32)
_CONVERTIBLE_EXTENSIONS = st.sampled_from(["docx", "odt", "rtf"])
_STORED_NAME = "document.docx"


class _RefusingConversion:
    def converted_file(self, source_path: Path, extension: str) -> bytes:
        refusal = f"{source_path.name} as {extension}"

        raise ConversionError(refusal)


class _ReadingConversion:
    def converted_file(self, source_path: Path, extension: str) -> bytes:
        _ = extension

        return source_path.read_bytes()


@settings(max_examples=10, deadline=None)
@given(_CONVERTIBLE_EXTENSIONS)
def test__converted_to_pdf_property_translates_a_refusal_into_a_bad_request(
    extension: str,
) -> None:
    stored = Path(_STORED_NAME)

    with pytest.raises(HTTPException) as raised:
        _ = _converted_to_pdf(_RefusingConversion(), stored, extension)

    assert raised.value.status_code == _BAD_REQUEST
    assert raised.value.detail == (
        f"Conversion failed: {_STORED_NAME} as {extension}"
    )


@settings(max_examples=25, deadline=None)
@given(_CONVERTIBLE_EXTENSIONS, _CONTENT)
def test__converted_to_pdf_property_hands_back_what_was_converted(
    extension: str, content: bytes
) -> None:
    with tempfile.TemporaryDirectory() as storage:
        stored = Path(storage) / _STORED_NAME
        _ = stored.write_bytes(content)

        converted = _converted_to_pdf(_ReadingConversion(), stored, extension)

    assert converted == content
