import tempfile
from pathlib import Path
from typing import Protocol

_SOURCE_STEM = "document"
_NO_OUTPUT = "LibreOffice produced no PDF"


class ConversionError(Exception):
    pass


class PdfExporter(Protocol):
    def export_pdf(
        self, source_path: Path, output_directory: str
    ) -> Path: ...


class PdfConversion:
    def __init__(self, pdf_exporter: PdfExporter) -> None:
        self._pdf_exporter: PdfExporter = pdf_exporter

    def converted(self, document: bytes, extension: str) -> bytes:
        with tempfile.TemporaryDirectory() as work_directory:
            source_path = (
                Path(work_directory) / f"{_SOURCE_STEM}.{extension}"
            )
            _ = source_path.write_bytes(document)

            exported_path = self._pdf_exporter.export_pdf(
                source_path, work_directory
            )

            if not exported_path.exists():
                raise ConversionError(_NO_OUTPUT)

            return exported_path.read_bytes()

    def converted_file(self, source_path: Path, extension: str) -> bytes:
        return self.converted(source_path.read_bytes(), extension)
