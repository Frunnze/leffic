from abc import ABC, abstractmethod
from typing import override

import textract

_SUPPORTED_EXTENSIONS = (
    "csv", "doc", "docx", "eml", "epub", "gif", "jpg", "jpeg", "json",
    "html", "htm", "mp3", "msg", "odt", "ogg", "pdf", "png", "pptx", "ps",
    "rtf", "tiff", "tif", "txt", "wav", "xlsx", "xls",
)


class TextExtractor(ABC):
    @abstractmethod
    def extract_text(self, filename: str, extension: str) -> str | None: ...


class GeneralTextExtractor(TextExtractor):
    @override
    def extract_text(self, filename: str, extension: str) -> str:
        text_bytes = textract.process(filename, extension=extension)

        return text_bytes.decode("utf-8", errors="ignore").strip()


class TextExtractorFactory:
    def __init__(self) -> None:
        super().__init__()
        self._registry: dict[str, TextExtractor] = {}

    def register_extractor(
        self, extension: str, extractor: TextExtractor
    ) -> None:
        self._registry[extension.lower()] = extractor

    def get_text_extractor(self, extension: str) -> TextExtractor | None:
        return self._registry.get(extension.lower())


text_extractor_factory = TextExtractorFactory()

for _extension in _SUPPORTED_EXTENSIONS:
    text_extractor_factory.register_extractor(
        _extension, GeneralTextExtractor()
    )
