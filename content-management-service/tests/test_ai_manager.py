from typing import Self

import pytest
from openai import OpenAIError

from shared.ai_manager import OpenAIManager, RequestCost
from shared.model_rates import GPT_4_1_NANO, MODEL_RATES

_SYSTEM_PROMPT = "You are helpful"
_USER_PROMPT = "Summarise this"
_EXPECTED_RETRY_CALL_COUNT = 2


class FakeUsageDetails:
    def __init__(self, cached_tokens: int) -> None:
        super().__init__()
        self.cached_tokens: int = cached_tokens


class FakeUsage:
    def __init__(
        self, input_tokens: int, output_tokens: int, cached_tokens: int
    ) -> None:
        super().__init__()
        self.input_tokens: int = input_tokens
        self.output_tokens: int = output_tokens
        self.input_tokens_details: FakeUsageDetails = FakeUsageDetails(
            cached_tokens
        )


class FakeResponse:
    def __init__(
        self, output_text: str, usage: FakeUsage | None = None
    ) -> None:
        super().__init__()
        self.output_text: str = output_text
        self.usage: FakeUsage | None = usage


class FakeResponses:
    def __init__(self, answers: list[object]) -> None:
        super().__init__()
        self.answers: list[object] = answers
        self.calls: list[object] = []

    def create(self, **kwargs: object) -> object:
        self.calls.append(kwargs)
        answer = self.answers.pop(0)

        if isinstance(answer, OpenAIError):
            raise answer

        return answer


class FakeClient:
    def __init__(self, answers: list[object]) -> None:
        super().__init__()
        self.responses: FakeResponses = FakeResponses(answers)

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_: object) -> None:
        return None


def _manager(answers: list[object], rates_for: str | None = None):  # noqa: ANN202
    client = FakeClient(answers)
    rates = MODEL_RATES.get(rates_for) if rates_for else None

    return OpenAIManager(
        client,  # pyright: ignore[reportArgumentType]
        "gpt-5-mini",
        RequestCost(rates),
    ), client


def test_returns_a_parsed_object_for_json_answers() -> None:
    manager, _ = _manager([FakeResponse('{"answer": 42}')])

    parsed, cost = manager.get_ai_res(_SYSTEM_PROMPT, _USER_PROMPT)

    assert parsed == {"answer": 42}
    assert cost is None


def test_retries_once_after_a_provider_error() -> None:
    manager, client = _manager(
        [OpenAIError("boom"), FakeResponse('{"ok": true}')]
    )

    parsed, _ = manager.get_ai_res(_SYSTEM_PROMPT, _USER_PROMPT)

    assert parsed == {"ok": True}
    assert len(client.responses.calls) == _EXPECTED_RETRY_CALL_COUNT


def test_raises_when_every_attempt_fails() -> None:
    manager, _ = _manager([OpenAIError("one"), OpenAIError("two")])

    with pytest.raises(RuntimeError, match="did not answer"):
        _ = manager.get_ai_res(_SYSTEM_PROMPT, _USER_PROMPT)


def test_computes_a_cost_when_rates_are_known() -> None:
    usage = FakeUsage(input_tokens=1000, output_tokens=500, cached_tokens=100)
    manager, _ = _manager(
        [FakeResponse('{"a": 1}', usage)], rates_for=GPT_4_1_NANO
    )

    _, cost = manager.get_ai_res(_SYSTEM_PROMPT, _USER_PROMPT)
    rates = MODEL_RATES[GPT_4_1_NANO]
    expected = (
        1000 * rates.input_token_cost
        + 500 * rates.output_token_cost
        + 100 * rates.cached_token_cost
    )

    assert cost == expected


def test_reports_no_cost_without_usage() -> None:
    rates = MODEL_RATES[GPT_4_1_NANO]

    assert RequestCost(rates).of(FakeResponse("x")) is None  # pyright: ignore[reportArgumentType]


def test_reports_no_cost_without_rates() -> None:
    usage = FakeUsage(input_tokens=1, output_tokens=1, cached_tokens=0)

    assert RequestCost(None).of(FakeResponse("x", usage)) is None  # pyright: ignore[reportArgumentType]


def test_history_answers_prepend_the_system_prompt() -> None:
    manager, client = _manager([FakeResponse("hello there")])

    answer = manager.get_ai_res_hist(
        _SYSTEM_PROMPT, [{"role": "user", "content": "hi"}]
    )

    assert answer == "hello there"
    assert len(client.responses.calls) == 1
