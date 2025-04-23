from abc import ABC, abstractmethod
import textract


class TextExtractor(ABC):
    @abstractmethod
    def extract_text(self, filename: str, extension: str) -> str | None:
        pass

class TextExtractorFactory:
    def __init__(self):
        self._registry = {}

    def register_extractor(self, extension: str, extractor: TextExtractor):
        self._registry[extension.lower()] = extractor

    def get_text_extractor(self, extension: str) -> TextExtractor:
        if extension.lower() in self._registry:
            return self._registry.get(extension.lower())

text_extractor_factory = TextExtractorFactory()
def register_extractor(extensions: list):
    def decorator(cls):
        extractor_class = cls()
        for extension in extensions:
            text_extractor_factory.register_extractor(extension, extractor_class)
        return cls
    return decorator

# Text extractors
@register_extractor([
    "csv", "doc", "docx", "eml", "epub", "gif", "jpg", "jpeg", "json",
    "html", "htm", "mp3", "msg", "odt", "ogg", "pdf", "png", "pptx", "ps",
    "rtf", "tiff", "tif", "txt", "wav", "xlsx", "xls"
])
class GeneralTextExtractor(TextExtractor):
    def extract_text(self, filename: str, extension: str) -> str:
        text_bytes = textract.process(
            filename, 
            output_encoding="UTF-8", 
            extension=extension
        )
        return text_bytes.decode("UTF-8")

if __name__ == "__main__":
    print(text_extractor_factory.get_text_extractor("docx").extract_text("thesis1.docx"))