import json
from typing import cast

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from openai import OpenAI, OpenAIError
from openai.types.responses import Response

from shared.ai_manager import (
    AIFactory,
    AiMessage,
    OpenAIManager,
    RequestCost,
)
from shared.model_rates import GPT_4_1_NANO, GPT_5_MINI, MODEL_RATES
from tests.test_ai_manager import FakeClient, FakeResponse, FakeUsage

_SYSTEM_PROMPT = "You are helpful"
_USER_PROMPT = "Summarise this"
_TOKENS = st.integers(min_value=0, max_value=10_000)
_SCALES = st.integers(min_value=2, max_value=8)
_TOLERANCE = 1e-9
def _as_response(fake: FakeResponse) -> Response:
    return cast("Response", cast("object", fake))


def _sent(client: FakeClient, key: str) -> object:
    return cast("dict[str, object]", client.responses.calls[0])[key]


_ANSWERS = st.dictionaries(
    st.sampled_from(["title", "body"]),
    st.text(min_size=1, max_size=8),
    min_size=1,
)


def _manager(
    answers: list[object], model: str = GPT_4_1_NANO
) -> tuple[OpenAIManager, FakeClient]:
    client = FakeClient(answers)
    manager = OpenAIManager(
        cast("OpenAI", cast("object", client)),
        model,
        MODEL_RATES.get(model),
    )

    return manager, client


@settings(max_examples=50)
@given(_TOKENS, _TOKENS, _TOKENS, _SCALES)
def test_of_property_scales_with_the_tokens_it_counts(
    input_tokens: int, output_tokens: int, cached: int, scale: int
) -> None:
    cost = RequestCost(MODEL_RATES[GPT_4_1_NANO])
    once = cost.of(
        _as_response(
            FakeResponse("", FakeUsage(input_tokens, output_tokens, cached))
        )
    )
    scaled = cost.of(
        _as_response(
            FakeResponse(
                "",
                FakeUsage(
                    input_tokens * scale,
                    output_tokens * scale,
                    cached * scale,
                ),
            )
        )
    )

    assert once is not None
    assert scaled is not None
    assert abs(scaled - once * scale) < _TOLERANCE


@settings(max_examples=25)
@given(_TOKENS, _TOKENS, _TOKENS)
def test___init___property_keeps_the_rates_it_was_handed(
    input_tokens: int, output_tokens: int, cached: int
) -> None:
    without_rates = RequestCost(None)

    assert without_rates.rates is None
    assert (
        without_rates.of(
            _as_response(
                FakeResponse(
                    "", FakeUsage(input_tokens, output_tokens, cached)
                )
            )
        )
        is None
    )


@settings(max_examples=25)
@given(_ANSWERS)
def test_get_ai_res_property_survives_one_failed_attempt(
    answer: dict[str, str],
) -> None:
    manager, _ = _manager(
        [OpenAIError("first attempt"), FakeResponse(json.dumps(answer))]
    )
    parsed, cost = manager.get_ai_res(_SYSTEM_PROMPT, _USER_PROMPT)

    assert parsed == answer
    assert cost is None


@settings(max_examples=25)
@given(_ANSWERS)
def test_get_ai_res_property_gives_up_once_every_attempt_failed(
    answer: dict[str, str],
) -> None:
    manager, _ = _manager(
        [OpenAIError("first"), OpenAIError("second")]
    )

    with pytest.raises(RuntimeError):
        _ = manager.get_ai_res(_SYSTEM_PROMPT, json.dumps(answer))


@settings(max_examples=25)
@given(st.lists(st.text(min_size=1, max_size=8), max_size=4))
def test_get_ai_res_hist_property_leads_with_the_system_prompt(
    turns: list[str],
) -> None:
    history = cast(
        "list[AiMessage]",
        [{"role": "user", "content": turn} for turn in turns],
    )
    manager, client = _manager([FakeResponse("answered")])
    spoken = manager.get_ai_res_hist(_SYSTEM_PROMPT, history)
    sent = cast("list[dict[str, object]]", _sent(client, "input"))

    assert spoken == "answered"
    assert sent[0]["content"] == _SYSTEM_PROMPT
    assert sent[1:] == history


@settings(max_examples=25)
@given(st.sampled_from([GPT_4_1_NANO, GPT_5_MINI]))
def test__answer_property_always_asks_for_the_configured_model(
    model: str,
) -> None:
    manager, client = _manager([FakeResponse("answered")], model)
    _ = manager._answer([])

    assert _sent(client, "model") == model


@settings(max_examples=25)
@given(st.one_of(st.none(), st.sampled_from([GPT_4_1_NANO, GPT_5_MINI])))
def test_get_ai_property_falls_back_to_the_default_model(
    model: str | None,
) -> None:
    built = AIFactory().get_ai(model)

    assert isinstance(built, OpenAIManager)
    assert built.model_name == (model or GPT_5_MINI)
