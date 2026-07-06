import pytest
import importlib.util
import sys
import os
from unittest.mock import patch, Mock

# Dynamically import extract_link_main_content from the file path
spec = importlib.util.spec_from_file_location(
    "link_extractor",
    os.path.join(os.path.dirname(__file__), '../file-processor-service/app/tools/link_extractor.py')
)
link_extractor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(link_extractor)
extract_link_main_content = link_extractor.extract_link_main_content

# Helper to mock requests.get
class MockResponse:
    def __init__(self, content, status_code=200):
        self.content = content.encode('utf-8')
        self.status_code = status_code
    def raise_for_status(self):
        if self.status_code != 200:
            raise Exception('HTTP Error')

@patch('requests.get')
def test_article_tag(mock_get):
    html = '<html><body><article>' + 'Article Content '*20 + '</article></body></html>'
    mock_get.return_value = MockResponse(html)
    result = extract_link_main_content('http://test.com')
    assert 'Article Content' in result

@patch('requests.get')
def test_main_tag(mock_get):
    html = '<html><body><main>' + 'Main Content '*20 + '</main></body></html>'
    mock_get.return_value = MockResponse(html)
    result = extract_link_main_content('http://test.com')
    assert 'Main Content' in result

@patch('requests.get')
def test_div_content_class(mock_get):
    html = '<html><body><div class="content">' + 'Content Div '*20 + '</div></body></html>'
    mock_get.return_value = MockResponse(html)
    result = extract_link_main_content('http://test.com')
    assert 'Content Div' in result

@patch('requests.get')
def test_section_main_class(mock_get):
    html = '<html><body><section class="main">' + 'Section Main '*20 + '</section></body></html>'
    mock_get.return_value = MockResponse(html)
    result = extract_link_main_content('http://test.com')
    assert 'Section Main' in result

@patch('requests.get')
def test_largest_div_fallback(mock_get):
    html = '<html><body><div>Short</div><div>' + 'A'*201 + '</div></body></html>'
    mock_get.return_value = MockResponse(html)
    result = extract_link_main_content('http://test.com')
    assert 'A'*201 in result

@patch('requests.get')
def test_no_main_content(mock_get):
    html = '<html><body><div>Short</div></body></html>'
    mock_get.return_value = MockResponse(html)
    result = extract_link_main_content('http://test.com')
    assert result is None

@patch('requests.get')
def test_error_handling(mock_get):
    mock_get.side_effect = Exception('Network error')
    result = extract_link_main_content('http://test.com')
    assert result is None

@patch('requests.get')
def test_status_code_error(mock_get):
    mock_get.return_value = MockResponse('<html></html>', status_code=404)
    result = extract_link_main_content('http://test.com')
    assert result is None

@patch('requests.get')
def test_custom_headers(mock_get):
    html = '<html><body><main>' + 'B'*250 + '</main></body></html>'
    mock_get.return_value = MockResponse(html)
    headers = {'User-Agent': 'pytest'}
    result = extract_link_main_content('http://test.com', headers=headers)
    assert 'B'*250 in result

@patch('requests.get')
def test_multiple_candidates(mock_get):
    html = '<html><body><main>' + 'C'*210 + '</main><article>' + 'D'*220 + '</article></body></html>'
    mock_get.return_value = MockResponse(html)
    result = extract_link_main_content('http://test.com')
    assert 'D'*220 in result or 'C'*210 in result

@patch('requests.get')
def test_section_content_class(mock_get):
    html = '<html><body><section class="content">' + 'E'*205 + '</section></body></html>'
    mock_get.return_value = MockResponse(html)
    result = extract_link_main_content('http://test.com')
    assert 'E'*205 in result

@patch('requests.get')
def test_div_main_class(mock_get):
    html = '<html><body><div class="main">' + 'F'*210 + '</div></body></html>'
    mock_get.return_value = MockResponse(html)
    result = extract_link_main_content('http://test.com')
    assert 'F'*210 in result

@patch('requests.get')
def test_article_short_content(mock_get):
    html = '<html><body><article>Short</article></body></html>'
    mock_get.return_value = MockResponse(html)
    result = extract_link_main_content('http://test.com')
    assert result is None

@patch('requests.get')
def test_main_short_content(mock_get):
    html = '<html><body><main>Short</main></body></html>'
    mock_get.return_value = MockResponse(html)
    result = extract_link_main_content('http://test.com')
    assert result is None

@patch('requests.get')
def test_div_large_content(mock_get):
    html = '<html><body><div>' + 'G'*250 + '</div></body></html>'
    mock_get.return_value = MockResponse(html)
    result = extract_link_main_content('http://test.com')
    assert 'G'*250 in result
