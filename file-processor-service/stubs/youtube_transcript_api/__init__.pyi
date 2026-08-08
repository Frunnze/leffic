from collections.abc import Iterator

class FetchedTranscriptSnippet:
    text: str

class Transcript:
    language_code: str
    is_generated: bool
    def fetch(self) -> list[FetchedTranscriptSnippet]: ...

class TranscriptList:
    def __iter__(self) -> Iterator[Transcript]: ...
    def find_manually_created_transcript(
        self, language_codes: list[str]
    ) -> Transcript: ...
    def find_generated_transcript(
        self, language_codes: list[str]
    ) -> Transcript: ...

class YouTubeTranscriptApi:
    def list(self, video_id: str) -> TranscriptList: ...

class TranscriptsDisabled(Exception): ...
class NoTranscriptFound(Exception): ...
