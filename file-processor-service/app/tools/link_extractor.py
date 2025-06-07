import requests
from bs4 import BeautifulSoup
import re


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