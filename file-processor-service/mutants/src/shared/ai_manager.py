from abc import ABC, abstractmethod
from typing import override

from openai import OpenAI, OpenAIError
from openai.types.responses import (
    EasyInputMessageParam,
    Response,
    ResponseInputItemParam,
)

from shared.json_extraction import get_dict_from_text
from shared.model_rates import GPT_5_MINI, MODEL_RATES, ModelRates

_ATTEMPTS = 2
_ALL_ATTEMPTS_FAILED = "The AI model did not answer"

AiMessage = ResponseInputItemParam


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict


class AIManager(ABC):
    @abstractmethod
    def get_ai_res(
        self, system_prompt: str, user_prompt: str
    ) -> tuple[dict[str, object], float | None]: ...

    @abstractmethod
    def get_ai_res_hist(
        self, system_prompt: str, history: list[AiMessage]
    ) -> str: ...
mutants_xǁRequestCostǁ__init____mutmut: MutantDict = {}  # type: ignore
mutants_xǁRequestCostǁof__mutmut: MutantDict = {}  # type: ignore


class RequestCost:
    @_mutmut_mutated(mutants_xǁRequestCostǁ__init____mutmut)
    def __init__(self, rates: ModelRates | None) -> None:
        super().__init__()
        self.rates: ModelRates | None = rates
    def xǁRequestCostǁ__init____mutmut_orig(self, rates: ModelRates | None) -> None:
        super().__init__()
        self.rates: ModelRates | None = rates
    def xǁRequestCostǁ__init____mutmut_1(self, rates: ModelRates | None) -> None:
        super().__init__()
        self.rates: ModelRates | None = None

    @_mutmut_mutated(mutants_xǁRequestCostǁof__mutmut)
    def of(self, response: Response) -> float | None:
        usage = response.usage

        if self.rates is None or usage is None:
            return None

        cached_tokens = usage.input_tokens_details.cached_tokens

        return (
            usage.input_tokens * self.rates.input_token_cost
            + usage.output_tokens * self.rates.output_token_cost
            + cached_tokens * self.rates.cached_token_cost
        )

    def xǁRequestCostǁof__mutmut_orig(self, response: Response) -> float | None:
        usage = response.usage

        if self.rates is None or usage is None:
            return None

        cached_tokens = usage.input_tokens_details.cached_tokens

        return (
            usage.input_tokens * self.rates.input_token_cost
            + usage.output_tokens * self.rates.output_token_cost
            + cached_tokens * self.rates.cached_token_cost
        )

    def xǁRequestCostǁof__mutmut_1(self, response: Response) -> float | None:
        usage = None

        if self.rates is None or usage is None:
            return None

        cached_tokens = usage.input_tokens_details.cached_tokens

        return (
            usage.input_tokens * self.rates.input_token_cost
            + usage.output_tokens * self.rates.output_token_cost
            + cached_tokens * self.rates.cached_token_cost
        )

    def xǁRequestCostǁof__mutmut_2(self, response: Response) -> float | None:
        usage = response.usage

        if self.rates is None and usage is None:
            return None

        cached_tokens = usage.input_tokens_details.cached_tokens

        return (
            usage.input_tokens * self.rates.input_token_cost
            + usage.output_tokens * self.rates.output_token_cost
            + cached_tokens * self.rates.cached_token_cost
        )

    def xǁRequestCostǁof__mutmut_3(self, response: Response) -> float | None:
        usage = response.usage

        if self.rates is not None or usage is None:
            return None

        cached_tokens = usage.input_tokens_details.cached_tokens

        return (
            usage.input_tokens * self.rates.input_token_cost
            + usage.output_tokens * self.rates.output_token_cost
            + cached_tokens * self.rates.cached_token_cost
        )

    def xǁRequestCostǁof__mutmut_4(self, response: Response) -> float | None:
        usage = response.usage

        if self.rates is None or usage is not None:
            return None

        cached_tokens = usage.input_tokens_details.cached_tokens

        return (
            usage.input_tokens * self.rates.input_token_cost
            + usage.output_tokens * self.rates.output_token_cost
            + cached_tokens * self.rates.cached_token_cost
        )

    def xǁRequestCostǁof__mutmut_5(self, response: Response) -> float | None:
        usage = response.usage

        if self.rates is None or usage is None:
            return None

        cached_tokens = None

        return (
            usage.input_tokens * self.rates.input_token_cost
            + usage.output_tokens * self.rates.output_token_cost
            + cached_tokens * self.rates.cached_token_cost
        )

    def xǁRequestCostǁof__mutmut_6(self, response: Response) -> float | None:
        usage = response.usage

        if self.rates is None or usage is None:
            return None

        cached_tokens = usage.input_tokens_details.cached_tokens

        return (
            usage.input_tokens * self.rates.input_token_cost
            + usage.output_tokens * self.rates.output_token_cost - cached_tokens * self.rates.cached_token_cost
        )

    def xǁRequestCostǁof__mutmut_7(self, response: Response) -> float | None:
        usage = response.usage

        if self.rates is None or usage is None:
            return None

        cached_tokens = usage.input_tokens_details.cached_tokens

        return (
            usage.input_tokens * self.rates.input_token_cost - usage.output_tokens * self.rates.output_token_cost
            + cached_tokens * self.rates.cached_token_cost
        )

    def xǁRequestCostǁof__mutmut_8(self, response: Response) -> float | None:
        usage = response.usage

        if self.rates is None or usage is None:
            return None

        cached_tokens = usage.input_tokens_details.cached_tokens

        return (
            usage.input_tokens / self.rates.input_token_cost
            + usage.output_tokens * self.rates.output_token_cost
            + cached_tokens * self.rates.cached_token_cost
        )

    def xǁRequestCostǁof__mutmut_9(self, response: Response) -> float | None:
        usage = response.usage

        if self.rates is None or usage is None:
            return None

        cached_tokens = usage.input_tokens_details.cached_tokens

        return (
            usage.input_tokens * self.rates.input_token_cost
            + usage.output_tokens / self.rates.output_token_cost
            + cached_tokens * self.rates.cached_token_cost
        )

    def xǁRequestCostǁof__mutmut_10(self, response: Response) -> float | None:
        usage = response.usage

        if self.rates is None or usage is None:
            return None

        cached_tokens = usage.input_tokens_details.cached_tokens

        return (
            usage.input_tokens * self.rates.input_token_cost
            + usage.output_tokens * self.rates.output_token_cost
            + cached_tokens / self.rates.cached_token_cost
        )

mutants_xǁRequestCostǁ__init____mutmut['_mutmut_orig'] = RequestCost.xǁRequestCostǁ__init____mutmut_orig # type: ignore # mutmut generated
mutants_xǁRequestCostǁ__init____mutmut['xǁRequestCostǁ__init____mutmut_1'] = RequestCost.xǁRequestCostǁ__init____mutmut_1 # type: ignore # mutmut generated

mutants_xǁRequestCostǁof__mutmut['_mutmut_orig'] = RequestCost.xǁRequestCostǁof__mutmut_orig # type: ignore # mutmut generated
mutants_xǁRequestCostǁof__mutmut['xǁRequestCostǁof__mutmut_1'] = RequestCost.xǁRequestCostǁof__mutmut_1 # type: ignore # mutmut generated
mutants_xǁRequestCostǁof__mutmut['xǁRequestCostǁof__mutmut_2'] = RequestCost.xǁRequestCostǁof__mutmut_2 # type: ignore # mutmut generated
mutants_xǁRequestCostǁof__mutmut['xǁRequestCostǁof__mutmut_3'] = RequestCost.xǁRequestCostǁof__mutmut_3 # type: ignore # mutmut generated
mutants_xǁRequestCostǁof__mutmut['xǁRequestCostǁof__mutmut_4'] = RequestCost.xǁRequestCostǁof__mutmut_4 # type: ignore # mutmut generated
mutants_xǁRequestCostǁof__mutmut['xǁRequestCostǁof__mutmut_5'] = RequestCost.xǁRequestCostǁof__mutmut_5 # type: ignore # mutmut generated
mutants_xǁRequestCostǁof__mutmut['xǁRequestCostǁof__mutmut_6'] = RequestCost.xǁRequestCostǁof__mutmut_6 # type: ignore # mutmut generated
mutants_xǁRequestCostǁof__mutmut['xǁRequestCostǁof__mutmut_7'] = RequestCost.xǁRequestCostǁof__mutmut_7 # type: ignore # mutmut generated
mutants_xǁRequestCostǁof__mutmut['xǁRequestCostǁof__mutmut_8'] = RequestCost.xǁRequestCostǁof__mutmut_8 # type: ignore # mutmut generated
mutants_xǁRequestCostǁof__mutmut['xǁRequestCostǁof__mutmut_9'] = RequestCost.xǁRequestCostǁof__mutmut_9 # type: ignore # mutmut generated
mutants_xǁRequestCostǁof__mutmut['xǁRequestCostǁof__mutmut_10'] = RequestCost.xǁRequestCostǁof__mutmut_10 # type: ignore # mutmut generated
mutants_xǁOpenAIManagerǁ__init____mutmut: MutantDict = {}  # type: ignore
mutants_xǁOpenAIManagerǁ_answer__mutmut: MutantDict = {}  # type: ignore


class OpenAIManager(AIManager):
    @_mutmut_mutated(mutants_xǁOpenAIManagerǁ__init____mutmut)
    def __init__(
        self, client: OpenAI, model_name: str, rates: ModelRates | None
    ) -> None:
        super().__init__()
        self.client: OpenAI = client
        self.model_name: str = model_name
        self.request_cost: RequestCost = RequestCost(rates)
    def xǁOpenAIManagerǁ__init____mutmut_orig(
        self, client: OpenAI, model_name: str, rates: ModelRates | None
    ) -> None:
        super().__init__()
        self.client: OpenAI = client
        self.model_name: str = model_name
        self.request_cost: RequestCost = RequestCost(rates)
    def xǁOpenAIManagerǁ__init____mutmut_1(
        self, client: OpenAI, model_name: str, rates: ModelRates | None
    ) -> None:
        super().__init__()
        self.client: OpenAI = None
        self.model_name: str = model_name
        self.request_cost: RequestCost = RequestCost(rates)
    def xǁOpenAIManagerǁ__init____mutmut_2(
        self, client: OpenAI, model_name: str, rates: ModelRates | None
    ) -> None:
        super().__init__()
        self.client: OpenAI = client
        self.model_name: str = None
        self.request_cost: RequestCost = RequestCost(rates)
    def xǁOpenAIManagerǁ__init____mutmut_3(
        self, client: OpenAI, model_name: str, rates: ModelRates | None
    ) -> None:
        super().__init__()
        self.client: OpenAI = client
        self.model_name: str = model_name
        self.request_cost: RequestCost = None
    def xǁOpenAIManagerǁ__init____mutmut_4(
        self, client: OpenAI, model_name: str, rates: ModelRates | None
    ) -> None:
        super().__init__()
        self.client: OpenAI = client
        self.model_name: str = model_name
        self.request_cost: RequestCost = RequestCost(None)

    @override
    def get_ai_res(
        self, system_prompt: str, user_prompt: str
    ) -> tuple[dict[str, object], float | None]:
        history: list[AiMessage] = [
            EasyInputMessageParam(
                role="developer", content=system_prompt
            ),
            EasyInputMessageParam(role="user", content=user_prompt),
        ]
        last_error: OpenAIError | None = None

        for _ in range(_ATTEMPTS):
            try:
                response = self._answer(history)
            except OpenAIError as error:
                last_error = error
                continue

            return (
                get_dict_from_text(response.output_text),
                self.request_cost.of(response),
            )

        raise RuntimeError(_ALL_ATTEMPTS_FAILED) from last_error

    @override
    def get_ai_res_hist(
        self, system_prompt: str, history: list[AiMessage]
    ) -> str:
        conversation: list[AiMessage] = [
            EasyInputMessageParam(
                role="developer", content=system_prompt
            ),
            *history,
        ]

        return self._answer(conversation).output_text

    @_mutmut_mutated(mutants_xǁOpenAIManagerǁ_answer__mutmut)
    def _answer(self, history: list[AiMessage]) -> Response:
        return self.client.responses.create(
            model=self.model_name, input=history
        )

    def xǁOpenAIManagerǁ_answer__mutmut_orig(self, history: list[AiMessage]) -> Response:
        return self.client.responses.create(
            model=self.model_name, input=history
        )

    def xǁOpenAIManagerǁ_answer__mutmut_1(self, history: list[AiMessage]) -> Response:
        return self.client.responses.create(
            model=None, input=history
        )

    def xǁOpenAIManagerǁ_answer__mutmut_2(self, history: list[AiMessage]) -> Response:
        return self.client.responses.create(
            model=self.model_name, input=None
        )

    def xǁOpenAIManagerǁ_answer__mutmut_3(self, history: list[AiMessage]) -> Response:
        return self.client.responses.create(
            input=history
        )

    def xǁOpenAIManagerǁ_answer__mutmut_4(self, history: list[AiMessage]) -> Response:
        return self.client.responses.create(
            model=self.model_name, )

mutants_xǁOpenAIManagerǁ__init____mutmut['_mutmut_orig'] = OpenAIManager.xǁOpenAIManagerǁ__init____mutmut_orig # type: ignore # mutmut generated
mutants_xǁOpenAIManagerǁ__init____mutmut['xǁOpenAIManagerǁ__init____mutmut_1'] = OpenAIManager.xǁOpenAIManagerǁ__init____mutmut_1 # type: ignore # mutmut generated
mutants_xǁOpenAIManagerǁ__init____mutmut['xǁOpenAIManagerǁ__init____mutmut_2'] = OpenAIManager.xǁOpenAIManagerǁ__init____mutmut_2 # type: ignore # mutmut generated
mutants_xǁOpenAIManagerǁ__init____mutmut['xǁOpenAIManagerǁ__init____mutmut_3'] = OpenAIManager.xǁOpenAIManagerǁ__init____mutmut_3 # type: ignore # mutmut generated
mutants_xǁOpenAIManagerǁ__init____mutmut['xǁOpenAIManagerǁ__init____mutmut_4'] = OpenAIManager.xǁOpenAIManagerǁ__init____mutmut_4 # type: ignore # mutmut generated

mutants_xǁOpenAIManagerǁ_answer__mutmut['_mutmut_orig'] = OpenAIManager.xǁOpenAIManagerǁ_answer__mutmut_orig # type: ignore # mutmut generated
mutants_xǁOpenAIManagerǁ_answer__mutmut['xǁOpenAIManagerǁ_answer__mutmut_1'] = OpenAIManager.xǁOpenAIManagerǁ_answer__mutmut_1 # type: ignore # mutmut generated
mutants_xǁOpenAIManagerǁ_answer__mutmut['xǁOpenAIManagerǁ_answer__mutmut_2'] = OpenAIManager.xǁOpenAIManagerǁ_answer__mutmut_2 # type: ignore # mutmut generated
mutants_xǁOpenAIManagerǁ_answer__mutmut['xǁOpenAIManagerǁ_answer__mutmut_3'] = OpenAIManager.xǁOpenAIManagerǁ_answer__mutmut_3 # type: ignore # mutmut generated
mutants_xǁOpenAIManagerǁ_answer__mutmut['xǁOpenAIManagerǁ_answer__mutmut_4'] = OpenAIManager.xǁOpenAIManagerǁ_answer__mutmut_4 # type: ignore # mutmut generated
mutants_xǁAIFactoryǁ__init____mutmut: MutantDict = {}  # type: ignore
mutants_xǁAIFactoryǁget_ai__mutmut: MutantDict = {}  # type: ignore


class AIFactory:
    @_mutmut_mutated(mutants_xǁAIFactoryǁ__init____mutmut)
    def __init__(self) -> None:
        super().__init__()
        self.openai_client: OpenAI = OpenAI()
    def xǁAIFactoryǁ__init____mutmut_orig(self) -> None:
        super().__init__()
        self.openai_client: OpenAI = OpenAI()
    def xǁAIFactoryǁ__init____mutmut_1(self) -> None:
        super().__init__()
        self.openai_client: OpenAI = None

    @_mutmut_mutated(mutants_xǁAIFactoryǁget_ai__mutmut)
    def get_ai(self, model: str | None = None) -> AIManager:
        model_name = model or GPT_5_MINI

        return OpenAIManager(
            self.openai_client, model_name, MODEL_RATES.get(model_name)
        )

    def xǁAIFactoryǁget_ai__mutmut_orig(self, model: str | None = None) -> AIManager:
        model_name = model or GPT_5_MINI

        return OpenAIManager(
            self.openai_client, model_name, MODEL_RATES.get(model_name)
        )

    def xǁAIFactoryǁget_ai__mutmut_1(self, model: str | None = None) -> AIManager:
        model_name = None

        return OpenAIManager(
            self.openai_client, model_name, MODEL_RATES.get(model_name)
        )

    def xǁAIFactoryǁget_ai__mutmut_2(self, model: str | None = None) -> AIManager:
        model_name = model and GPT_5_MINI

        return OpenAIManager(
            self.openai_client, model_name, MODEL_RATES.get(model_name)
        )

    def xǁAIFactoryǁget_ai__mutmut_3(self, model: str | None = None) -> AIManager:
        model_name = model or GPT_5_MINI

        return OpenAIManager(
            None, model_name, MODEL_RATES.get(model_name)
        )

    def xǁAIFactoryǁget_ai__mutmut_4(self, model: str | None = None) -> AIManager:
        model_name = model or GPT_5_MINI

        return OpenAIManager(
            self.openai_client, None, MODEL_RATES.get(model_name)
        )

    def xǁAIFactoryǁget_ai__mutmut_5(self, model: str | None = None) -> AIManager:
        model_name = model or GPT_5_MINI

        return OpenAIManager(
            self.openai_client, model_name, None
        )

    def xǁAIFactoryǁget_ai__mutmut_6(self, model: str | None = None) -> AIManager:
        model_name = model or GPT_5_MINI

        return OpenAIManager(
            model_name, MODEL_RATES.get(model_name)
        )

    def xǁAIFactoryǁget_ai__mutmut_7(self, model: str | None = None) -> AIManager:
        model_name = model or GPT_5_MINI

        return OpenAIManager(
            self.openai_client, MODEL_RATES.get(model_name)
        )

    def xǁAIFactoryǁget_ai__mutmut_8(self, model: str | None = None) -> AIManager:
        model_name = model or GPT_5_MINI

        return OpenAIManager(
            self.openai_client, model_name, )

    def xǁAIFactoryǁget_ai__mutmut_9(self, model: str | None = None) -> AIManager:
        model_name = model or GPT_5_MINI

        return OpenAIManager(
            self.openai_client, model_name, MODEL_RATES.get(None)
        )

mutants_xǁAIFactoryǁ__init____mutmut['_mutmut_orig'] = AIFactory.xǁAIFactoryǁ__init____mutmut_orig # type: ignore # mutmut generated
mutants_xǁAIFactoryǁ__init____mutmut['xǁAIFactoryǁ__init____mutmut_1'] = AIFactory.xǁAIFactoryǁ__init____mutmut_1 # type: ignore # mutmut generated

mutants_xǁAIFactoryǁget_ai__mutmut['_mutmut_orig'] = AIFactory.xǁAIFactoryǁget_ai__mutmut_orig # type: ignore # mutmut generated
mutants_xǁAIFactoryǁget_ai__mutmut['xǁAIFactoryǁget_ai__mutmut_1'] = AIFactory.xǁAIFactoryǁget_ai__mutmut_1 # type: ignore # mutmut generated
mutants_xǁAIFactoryǁget_ai__mutmut['xǁAIFactoryǁget_ai__mutmut_2'] = AIFactory.xǁAIFactoryǁget_ai__mutmut_2 # type: ignore # mutmut generated
mutants_xǁAIFactoryǁget_ai__mutmut['xǁAIFactoryǁget_ai__mutmut_3'] = AIFactory.xǁAIFactoryǁget_ai__mutmut_3 # type: ignore # mutmut generated
mutants_xǁAIFactoryǁget_ai__mutmut['xǁAIFactoryǁget_ai__mutmut_4'] = AIFactory.xǁAIFactoryǁget_ai__mutmut_4 # type: ignore # mutmut generated
mutants_xǁAIFactoryǁget_ai__mutmut['xǁAIFactoryǁget_ai__mutmut_5'] = AIFactory.xǁAIFactoryǁget_ai__mutmut_5 # type: ignore # mutmut generated
mutants_xǁAIFactoryǁget_ai__mutmut['xǁAIFactoryǁget_ai__mutmut_6'] = AIFactory.xǁAIFactoryǁget_ai__mutmut_6 # type: ignore # mutmut generated
mutants_xǁAIFactoryǁget_ai__mutmut['xǁAIFactoryǁget_ai__mutmut_7'] = AIFactory.xǁAIFactoryǁget_ai__mutmut_7 # type: ignore # mutmut generated
mutants_xǁAIFactoryǁget_ai__mutmut['xǁAIFactoryǁget_ai__mutmut_8'] = AIFactory.xǁAIFactoryǁget_ai__mutmut_8 # type: ignore # mutmut generated
mutants_xǁAIFactoryǁget_ai__mutmut['xǁAIFactoryǁget_ai__mutmut_9'] = AIFactory.xǁAIFactoryǁget_ai__mutmut_9 # type: ignore # mutmut generated


ai_factory = AIFactory()
