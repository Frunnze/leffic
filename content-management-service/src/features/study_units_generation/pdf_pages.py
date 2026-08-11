import io

from pypdf import PdfReader, PdfWriter


class PageSelectionError(Exception):
    pass


class PdfPageSelection:
    @staticmethod
    def sliced(document: bytes, first_page: int, last_page: int) -> bytes:
        reader = PdfReader(io.BytesIO(document))
        page_count = len(reader.pages)

        if first_page > page_count:
            refusal = f"The document has only {page_count} pages"

            raise PageSelectionError(refusal)

        writer = PdfWriter()

        for page in reader.pages[first_page - 1 : last_page]:
            _ = writer.add_page(page)

        selection = io.BytesIO()
        _ = writer.write(selection)

        return selection.getvalue()
