import io
import subprocess
from pathlib import Path

from pypdf import PdfReader, PdfWriter

_PAGE_SIDE = 200


class PdfDocuments:
    @staticmethod
    def blank(page_count: int) -> bytes:
        writer = PdfWriter()

        for _ in range(page_count):
            _ = writer.add_blank_page(width=_PAGE_SIDE, height=_PAGE_SIDE)

        written = io.BytesIO()
        _ = writer.write(written)

        return written.getvalue()

    @staticmethod
    def page_count(document: bytes) -> int:
        return len(PdfReader(io.BytesIO(document)).pages)


class DocumentRecorder:
    def __init__(self, documents: list[bytes]) -> None:
        self.documents: list[bytes] = documents
        self.extensions: list[str] = []

    def __call__(
        self, filename: str, extension: str = "", **_unused: object
    ) -> bytes:
        self.extensions.append(extension)
        self.documents.append(Path(filename).read_bytes())

        return b""


class LibreOfficeStub:
    def __init__(self, page_count: int) -> None:
        self.page_count: int = page_count
        self.converted_sources: list[str] = []

    def __call__(
        self, command: list[str], **_unused: object
    ) -> subprocess.CompletedProcess[bytes]:
        output_directory = Path(command[command.index("--outdir") + 1])
        source = Path(command[-1])
        self.converted_sources.append(source.name)
        written = output_directory / f"{source.stem}.pdf"
        _ = written.write_bytes(PdfDocuments.blank(self.page_count))

        return subprocess.CompletedProcess(
            args=command, returncode=0, stderr=b""
        )
