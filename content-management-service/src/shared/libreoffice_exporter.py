import subprocess
from pathlib import Path

from shared.pdf_conversion import ConversionError, PdfConversion

_PDF_EXTENSION = "pdf"
_CONVERSION_TIMEOUT_SECONDS = 120


class LibreOfficeExporter:
    def export_pdf(self, source_path: Path, output_directory: str) -> Path:
        completed_conversion = subprocess.run(
            self._command(source_path, output_directory),
            capture_output=True,
            check=False,
            timeout=_CONVERSION_TIMEOUT_SECONDS,
        )

        if completed_conversion.returncode != 0:
            raise ConversionError(completed_conversion.stderr.decode())

        exported_name = f"{source_path.stem}.{_PDF_EXTENSION}"

        return Path(output_directory) / exported_name

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


def provide_pdf_conversion() -> PdfConversion:
    return PdfConversion(LibreOfficeExporter())
