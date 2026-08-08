from dataclasses import dataclass

_TOKENS_PER_PRICE_UNIT = 1000000


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict


@dataclass(frozen=True)
class ModelRates:
    input_token_cost: float
    output_token_cost: float
    cached_token_cost: float


GPT_4_1_NANO = "gpt-4.1-nano"
GPT_5_MINI = "gpt-5-mini"

MODEL_RATES: dict[str, ModelRates] = {
    GPT_4_1_NANO: ModelRates(
        input_token_cost=0.100 / _TOKENS_PER_PRICE_UNIT,
        output_token_cost=0.025 / _TOKENS_PER_PRICE_UNIT,
        cached_token_cost=0.400 / _TOKENS_PER_PRICE_UNIT,
    ),
}
