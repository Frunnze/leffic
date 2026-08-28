from typing import Self, cast

import pytest
from openai import OpenAIError

from shared.ai_manager import (
    OpenAIManager,
    RequestCost,
    create_openai_factory,
)
from shared.model_rates import GPT_4_1_NANO, MODEL_RATES

_SYSTEM_PROMPT = "You are helpful"
_USER_PROMPT = "Summarise this"


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


def test_the_factory_defaults_to_the_mini_model() -> None:
    manager = create_openai_factory().get_ai()

    assert isinstance(manager, OpenAIManager)
    assert manager.model_name == "gpt-5-mini"


def test_the_factory_honours_a_named_model() -> None:
    manager = create_openai_factory().get_ai(GPT_4_1_NANO)

    assert isinstance(manager, OpenAIManager)
    assert manager.model_name == GPT_4_1_NANO


def test_the_system_and_user_prompts_both_reach_the_model() -> None:
    manager, client = _manager([FakeResponse('{"a": 1}')])

    _ = manager.get_ai_res(_SYSTEM_PROMPT, _USER_PROMPT)

    sent = str(client.responses.calls[0])

    assert _SYSTEM_PROMPT in sent
    assert _USER_PROMPT in sent


def test_the_configured_model_reaches_the_client() -> None:
    manager, client = _manager([FakeResponse('{"a": 1}')])

    _ = manager.get_ai_res(_SYSTEM_PROMPT, _USER_PROMPT)
    sent = cast("dict[str, object]", client.responses.calls[0])

    assert sent["model"] == "gpt-5-mini"
    assert sent["input"]


def test_the_factory_reads_the_api_key_from_the_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "a-configured-key")

    manager = create_openai_factory().get_ai()

    assert isinstance(manager, OpenAIManager)
    assert manager.client.api_key == "a-configured-key"


def test_the_factory_gives_the_manager_its_own_client() -> None:
    factory = create_openai_factory()
    manager = factory.get_ai()
    another_manager = factory.get_ai()

    assert isinstance(manager, OpenAIManager)
    assert isinstance(another_manager, OpenAIManager)
    assert another_manager.client is manager.client


def test_a_known_model_gets_its_rates() -> None:
    manager = create_openai_factory().get_ai(GPT_4_1_NANO)

    assert isinstance(manager, OpenAIManager)
    assert manager.request_cost.rates == MODEL_RATES[GPT_4_1_NANO]


def test_an_unknown_model_has_no_rates() -> None:
    manager = create_openai_factory().get_ai("gpt-unknown")

    assert isinstance(manager, OpenAIManager)
    assert manager.request_cost.rates is None
