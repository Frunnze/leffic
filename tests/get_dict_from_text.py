import pytest
from ai_manager import get_dict_from_text
import demjson3

def test_basic_extraction():
    text = "Prefix\n{\"key\": \"value\"}\tSuffix"
    assert get_dict_from_text(text) == {"key": "value"}

def test_with_whitespace():
    text = "Start\n\t{\n\t\t'key': 'value'\n\t}\tEnd"
    assert get_dict_from_text(text) == {'key': 'value'}

def test_multiple_braces_valid_structure():
    text = "outer { 'inner': { 'nested': 1 } } end"
    assert get_dict_from_text(text) == {'inner': {'nested': 1}}

def test_dict_at_start():
    text = "{'a': 1} some text"
    assert get_dict_from_text(text) == {'a': 1}

def test_dict_at_end():
    text = "some text {'b': 2}"
    assert get_dict_from_text(text) == {'b': 2}

def test_no_opening_brace():
    text = "no opening brace here }"
    with pytest.raises(demjson3.JSONDecodeError):
        get_dict_from_text(text)

def test_no_closing_brace():
    text = "{ 'key': 'value' "
    with pytest.raises(demjson3.JSONDecodeError):
        get_dict_from_text(text)

def test_invalid_json_syntax():
    text = "text { 'key': } more text"
    with pytest.raises(demjson3.JSONDecodeError):
        get_dict_from_text(text)

def test_nested_structures_and_commas():
    text = """
    Data {
        'user': {
            'id': 101,
            'name': 'Test'
        },
        'scores': [95, 87, 89]
    }
    """
    expected = {
        'user': {'id': 101, 'name': 'Test'},
        'scores': [95, 87, 89]
    }
    assert get_dict_from_text(text) == expected

def test_unquoted_keys_allowed_by_demjson3():
    text = "{ key: 'value', number: 123 }"
    assert get_dict_from_text(text) == {'key': 'value', 'number': 123}