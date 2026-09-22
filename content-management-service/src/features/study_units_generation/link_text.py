from features.study_units_generation.webpage_extractor import (
    extract_link_main_content,
)
from features.study_units_generation.youtube_transcript import (
    get_youtube_transcript_auto,
)

_YOUTUBE_HOST = "youtube.com"


class WebLinkText:
    def text_from_link(self, link: str) -> str:
        if _YOUTUBE_HOST in link:
            transcript = get_youtube_transcript_auto(link)

            if transcript:
                return transcript

        return extract_link_main_content(link) or ""
