import demjson3
import pytest
from demjson3 import JSONDecodeError

from shared.json_extraction import get_dict_from_text


def _decode_to_a_list(text: str) -> object:
    return [text]


def test_extracts_a_plain_object() -> None:
    assert get_dict_from_text('Prefix\n{"key": "value"}\tSuffix') == {
        "key": "value"
    }


def test_ignores_surrounding_whitespace_and_tabs() -> None:
    text = "Start\n\t{\n\t\t'key': 'value'\n\t}\tEnd"

    assert get_dict_from_text(text) == {"key": "value"}


def test_tabs_are_left_alone_inside_values() -> None:
    assert get_dict_from_text('{"key": "one\ttwo"}') == {"key": "one\ttwo"}


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


def test_rejects_an_answer_that_is_not_an_object(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(demjson3, "decode", _decode_to_a_list)

    with pytest.raises(TypeError, match="did not answer with an object"):
        _ = get_dict_from_text("{}")


def test_newlines_inside_the_object_are_removed() -> None:
    assert get_dict_from_text('{"key":\n"value"}') == {"key": "value"}


def test_a_multi_line_string_value_is_joined_up() -> None:
    assert get_dict_from_text('{"key": "one\ntwo"}') == {"key": "onetwo"}


def test_text_straight_after_the_object_is_left_out() -> None:
    assert get_dict_from_text('{"a": 1}tail') == {"a": 1}
