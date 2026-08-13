import subprocess
from pathlib import Path
from unittest import mock

import pytest

from shared.pdf_conversion import ConversionError, PdfConversion

_PDF_BYTES = b"%PDF-1.7 converted"


class LibreOfficeStub:
    def __init__(
        self, produced: bytes | None = _PDF_BYTES, exit_code: int = 0
    ) -> None:
        self.produced: bytes | None = produced
        self.exit_code: int = exit_code
        self.commands: list[list[str]] = []
        self.sources: list[bytes] = []

    def __call__(
        self, command: list[str], **_unused: object
    ) -> subprocess.CompletedProcess[bytes]:
        self.commands.append(command)
        self.sources.append(Path(command[-1]).read_bytes())

        if self.produced is not None:
            output_directory = Path(command[command.index("--outdir") + 1])
            source = Path(command[-1])
            written = output_directory / f"{source.stem}.pdf"
            _ = written.write_bytes(self.produced)

        return subprocess.CompletedProcess(
            args=command, returncode=self.exit_code, stderr=b"unreadable"
        )


def test_a_converted_document_comes_back_as_pdf_bytes() -> None:
    libreoffice = LibreOfficeStub()

    with mock.patch.object(subprocess, "run", libreoffice):
        converted = PdfConversion.converted(b"docx payload", "docx")

    assert converted == _PDF_BYTES


def test_the_document_is_handed_to_libreoffice_with_its_extension() -> None:
    libreoffice = LibreOfficeStub()

    with mock.patch.object(subprocess, "run", libreoffice):
        _ = PdfConversion.converted(b"pptx payload", "pptx")

    assert Path(libreoffice.commands[0][-1]).suffix == ".pptx"


def test_the_document_is_written_where_libreoffice_reads_it() -> None:
    libreoffice = LibreOfficeStub()

    with mock.patch.object(subprocess, "run", libreoffice):
        _ = PdfConversion.converted(b"docx payload", "docx")

    assert libreoffice.sources == [b"docx payload"]


def test_a_failed_conversion_reports_what_libreoffice_wrote() -> None:
    libreoffice = LibreOfficeStub(produced=None, exit_code=1)

    with (
        mock.patch.object(subprocess, "run", libreoffice),
        pytest.raises(ConversionError) as refusal,
    ):
        _ = PdfConversion.converted(b"docx payload", "docx")

    assert "unreadable" in str(refusal.value)


def test_a_conversion_that_writes_no_pdf_is_refused() -> None:
    libreoffice = LibreOfficeStub(produced=None)

    with (
        mock.patch.object(subprocess, "run", libreoffice),
        pytest.raises(ConversionError) as refusal,
    ):
        _ = PdfConversion.converted(b"docx payload", "docx")

    assert str(refusal.value) == "LibreOffice produced no PDF"
