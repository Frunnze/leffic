from abc import ABC, abstractmethod
from typing import override

import textract

_SUPPORTED_EXTENSIONS = (
    "csv", "doc", "docx", "eml", "epub", "gif", "jpg", "jpeg", "json",
    "html", "htm", "mp3", "msg", "odt", "ogg", "pdf", "png", "pptx", "ps",
    "rtf", "tiff", "tif", "txt", "wav", "xlsx", "xls",
)


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict


class TextExtractor(ABC):
    @abstractmethod
    def extract_text(self, filename: str, extension: str) -> str | None: ...


class GeneralTextExtractor(TextExtractor):
    @override
    def extract_text(self, filename: str, extension: str) -> str:
        text_bytes = textract.process(filename, extension=extension)

        return text_bytes.decode("utf-8", errors="ignore").strip()
mutants_xǁTextExtractorFactoryǁ__init____mutmut: MutantDict = {}  # type: ignore
mutants_xǁTextExtractorFactoryǁregister_extractor__mutmut: MutantDict = {}  # type: ignore
mutants_xǁTextExtractorFactoryǁget_text_extractor__mutmut: MutantDict = {}  # type: ignore


class TextExtractorFactory:
    @_mutmut_mutated(mutants_xǁTextExtractorFactoryǁ__init____mutmut)
    def __init__(self) -> None:
        super().__init__()
        self._registry: dict[str, TextExtractor] = {}
    def xǁTextExtractorFactoryǁ__init____mutmut_orig(self) -> None:
        super().__init__()
        self._registry: dict[str, TextExtractor] = {}
    def xǁTextExtractorFactoryǁ__init____mutmut_1(self) -> None:
        super().__init__()
        self._registry: dict[str, TextExtractor] = None

    @_mutmut_mutated(mutants_xǁTextExtractorFactoryǁregister_extractor__mutmut)
    def register_extractor(
        self, extension: str, extractor: TextExtractor
    ) -> None:
        self._registry[extension.lower()] = extractor

    def xǁTextExtractorFactoryǁregister_extractor__mutmut_orig(
        self, extension: str, extractor: TextExtractor
    ) -> None:
        self._registry[extension.lower()] = extractor

    def xǁTextExtractorFactoryǁregister_extractor__mutmut_1(
        self, extension: str, extractor: TextExtractor
    ) -> None:
        self._registry[extension.lower()] = None

    def xǁTextExtractorFactoryǁregister_extractor__mutmut_2(
        self, extension: str, extractor: TextExtractor
    ) -> None:
        self._registry[extension.upper()] = extractor

    @_mutmut_mutated(mutants_xǁTextExtractorFactoryǁget_text_extractor__mutmut)
    def get_text_extractor(self, extension: str) -> TextExtractor | None:
        return self._registry.get(extension.lower())

    def xǁTextExtractorFactoryǁget_text_extractor__mutmut_orig(self, extension: str) -> TextExtractor | None:
        return self._registry.get(extension.lower())

    def xǁTextExtractorFactoryǁget_text_extractor__mutmut_1(self, extension: str) -> TextExtractor | None:
        return self._registry.get(None)

    def xǁTextExtractorFactoryǁget_text_extractor__mutmut_2(self, extension: str) -> TextExtractor | None:
        return self._registry.get(extension.upper())

mutants_xǁTextExtractorFactoryǁ__init____mutmut['_mutmut_orig'] = TextExtractorFactory.xǁTextExtractorFactoryǁ__init____mutmut_orig # type: ignore # mutmut generated
mutants_xǁTextExtractorFactoryǁ__init____mutmut['xǁTextExtractorFactoryǁ__init____mutmut_1'] = TextExtractorFactory.xǁTextExtractorFactoryǁ__init____mutmut_1 # type: ignore # mutmut generated

mutants_xǁTextExtractorFactoryǁregister_extractor__mutmut['_mutmut_orig'] = TextExtractorFactory.xǁTextExtractorFactoryǁregister_extractor__mutmut_orig # type: ignore # mutmut generated
mutants_xǁTextExtractorFactoryǁregister_extractor__mutmut['xǁTextExtractorFactoryǁregister_extractor__mutmut_1'] = TextExtractorFactory.xǁTextExtractorFactoryǁregister_extractor__mutmut_1 # type: ignore # mutmut generated
mutants_xǁTextExtractorFactoryǁregister_extractor__mutmut['xǁTextExtractorFactoryǁregister_extractor__mutmut_2'] = TextExtractorFactory.xǁTextExtractorFactoryǁregister_extractor__mutmut_2 # type: ignore # mutmut generated

mutants_xǁTextExtractorFactoryǁget_text_extractor__mutmut['_mutmut_orig'] = TextExtractorFactory.xǁTextExtractorFactoryǁget_text_extractor__mutmut_orig # type: ignore # mutmut generated
mutants_xǁTextExtractorFactoryǁget_text_extractor__mutmut['xǁTextExtractorFactoryǁget_text_extractor__mutmut_1'] = TextExtractorFactory.xǁTextExtractorFactoryǁget_text_extractor__mutmut_1 # type: ignore # mutmut generated
mutants_xǁTextExtractorFactoryǁget_text_extractor__mutmut['xǁTextExtractorFactoryǁget_text_extractor__mutmut_2'] = TextExtractorFactory.xǁTextExtractorFactoryǁget_text_extractor__mutmut_2 # type: ignore # mutmut generated


text_extractor_factory = TextExtractorFactory()

for _extension in _SUPPORTED_EXTENSIONS:
    text_extractor_factory.register_extractor(
        _extension, GeneralTextExtractor()
    )
