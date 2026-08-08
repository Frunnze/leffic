import requests
from bs4 import BeautifulSoup
import re
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from urllib.parse import urlparse, parse_qs


def extract_video_id(url):
    parsed_url = urlparse(url)
    
    if parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
        query = parse_qs(parsed_url.query)
        return query.get('v', [None])[0]
    elif parsed_url.hostname == 'youtu.be':
        return parsed_url.path.lstrip('/')
    
    return None


def get_youtube_transcript_auto(link, preferred_langs=['en']):
    try:
        video_id = extract_video_id(link)
        if not video_id: return None

        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        # Try manually created transcripts in preferred languages
        for lang in preferred_langs:
            try:
                transcript = transcript_list.find_manually_created_transcript([lang])
                return ' '.join([entry.text for entry in transcript.fetch()])
            except:
                pass

        # Try auto-generated transcripts in preferred languages
        for lang in preferred_langs:
            try:
                transcript = transcript_list.find_generated_transcript([lang])
                return ' '.join([entry.text for entry in transcript.fetch()])
            except:
                pass

        # Fallback: any manually created transcript
        if transcript_list._manually_created_transcripts:
            transcript = list(transcript_list._manually_created_transcripts.values())[0]
            return ' '.join([entry.text for entry in transcript.fetch()])

        # Fallback: any auto-generated transcript
        if transcript_list._generated_transcripts:
            transcript = list(transcript_list._generated_transcripts.values())[0]
            return ' '.join([entry.text for entry in transcript.fetch()])

    except (TranscriptsDisabled, NoTranscriptFound):
        print("No transcript available.")
    except Exception as e:
        print(f"Unexpected error: {e}")

    return None


def extract_link_main_content(url, headers=None):
    """
    Extracts the main readable content from a web page.
    
    Args:
        url (str): The URL of the web page.
        headers (dict, optional): Optional headers to include in the request.
    
    Returns:
        str: Extracted main text content of the page, or an error message.
    """
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Try common containers for main content
        main_candidates = [
            soup.find('article'),
            soup.find('main'),
            soup.find('div', class_=re.compile(r'(content|main|article|body)', re.I)),
            soup.find('section', class_=re.compile(r'(content|main|article|body)', re.I))
        ]

        for candidate in main_candidates:
            if candidate and len(candidate.get_text(strip=True)) > 200:
                return candidate.get_text(separator='\n', strip=True)

        # Fallback: largest div by text length
        divs = soup.find_all('div')
        largest_div = max(divs, key=lambda d: len(d.get_text(strip=True)), default=None)

        if largest_div and len(largest_div.get_text(strip=True)) > 200:
            return largest_div.get_text(separator='\n', strip=True)

        return None

    except Exception as e:
        return None