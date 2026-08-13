import subprocess
import tempfile
from pathlib import Path

_PDF_EXTENSION = "pdf"
_SOURCE_STEM = "document"
_CONVERSION_TIMEOUT_SECONDS = 120
_NO_OUTPUT = "LibreOffice produced no PDF"


class ConversionError(Exception):
    pass


class PdfConversion:
    @staticmethod
    def converted(document: bytes, extension: str) -> bytes:
        with tempfile.TemporaryDirectory() as work_directory:
            source_path = (
                Path(work_directory) / f"{_SOURCE_STEM}.{extension}"
            )
            _ = source_path.write_bytes(document)

            return PdfConversion._written_pdf(source_path, work_directory)

    @staticmethod
    def _written_pdf(source_path: Path, output_directory: str) -> bytes:
        result = subprocess.run(
            PdfConversion._command(source_path, output_directory),
            capture_output=True,
            check=False,
            timeout=_CONVERSION_TIMEOUT_SECONDS,
        )

        if result.returncode != 0:
            raise ConversionError(result.stderr.decode())

        converted_path = (
            Path(output_directory) / f"{_SOURCE_STEM}.{_PDF_EXTENSION}"
        )

        if not converted_path.exists():
            raise ConversionError(_NO_OUTPUT)

        return converted_path.read_bytes()

    @staticmethod
    def _command(source_path: Path, output_directory: str) -> list[str]:
        return [
            "libreoffice",
            "--headless",
            "--convert-to",
            _PDF_EXTENSION,
            "--outdir",
            output_directory,
            str(source_path),
        ]
