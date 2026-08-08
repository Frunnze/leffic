import pytest
from demjson3 import JSONDecodeError

from src.shared.json_extraction import get_dict_from_text


def test_extracts_a_plain_object() -> None:
    assert get_dict_from_text('Prefix\n{"key": "value"}\tSuffix') == {
        "key": "value"
    }


def test_ignores_surrounding_whitespace_and_tabs() -> None:
    text = "Start\n\t{\n\t\t'key': 'value'\n\t}\tEnd"

    assert get_dict_from_text(text) == {"key": "value"}


def test_keeps_the_outermost_braces() -> None:
    text = "outer { 'inner': { 'nested': 1 } } end"

    assert get_dict_from_text(text) == {"inner": {"nested": 1}}


def test_extracts_an_object_at_the_start() -> None:
    assert get_dict_from_text("{'a': 1} some text") == {"a": 1}


def test_extracts_an_object_at_the_end() -> None:
    assert get_dict_from_text("some text {'b': 2}") == {"b": 2}


def test_rejects_text_without_any_object() -> None:
    with pytest.raises(JSONDecodeError, match="No value to decode"):
        _ = get_dict_from_text("no object here")
