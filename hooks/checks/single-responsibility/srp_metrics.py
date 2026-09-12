"""Language-independent metrics and deliberately conservative SRP scoring."""

from dataclasses import asdict, dataclass, field

from srp_effects import effect_domains
from srp_flow import effect_flow

THRESHOLD = 0.5
# Evidence scores stay stable when the commit policy becomes stricter.
HIGH_CONFIDENCE = 0.8


@dataclass
class CallableFacts:
    name: str
    line: int
    owner: str
    lines: int = 0
    statements: int = 0
    complexity: int = 1
    nesting: int = 0
    parameters: int = 0
    locals: int = 0
    calls: list[str] = field(default_factory=list)
    call_aliases: dict[str, str] = field(default_factory=dict)
    delegated_effects: list[str] = field(default_factory=list)
    binding_stable: bool = True
    resources: list[str] = field(default_factory=list)
    links: list[str] = field(default_factory=list)
    references: list[str] = field(default_factory=list)
    foreign_data: list[str] = field(default_factory=list)
    flow: list[dict] = field(default_factory=list)
    client_only: bool = False


def ramp(value: float, start: float, end: float) -> float:
    return max(0.0, min(1.0, (value - start) / (end - start)))


def burden(facts: CallableFacts) -> dict[str, float]:
    return {
        "method_length": ramp(facts.lines, 25, 80),
        "statements": ramp(facts.statements, 15, 50),
        "complexity": ramp(facts.complexity, 4, 15),
        "nesting": ramp(facts.nesting, 2, 5),
        "fan_out": ramp(len(set(facts.calls)), 4, 12),
        "parameters": ramp(facts.parameters, 4, 9),
        "locals": ramp(facts.locals, 6, 18),
    }


def implementation_burden(signals: dict[str, float]) -> float:
    weights = (0.25, 0.20, 0.20, 0.10, 0.10, 0.075, 0.075)
    return sum(
        weight * value
        for weight, value in zip(
            weights,
            signals.values(),
            strict=True,
        )
    )


def callable_score(facts: CallableFacts) -> dict:
    signals = burden(facts)
    structural = implementation_burden(signals)
    direct = effect_domains(facts.calls)
    delegated = effect_domains(facts.delegated_effects)
    domains = effect_domains(facts.calls + facts.delegated_effects)
    strong_domains = [name for name, calls in domains.items() if len(calls) >= 2]
    mixed = min(1.0, len(strong_domains) / 2)
    score = 0.65 * mixed + 0.35 * structural
    corroboration = sum(value >= 0.5 for value in signals.values())
    flow = effect_flow(facts.flow)
    if len(strong_domains) < 2 or corroboration < 2 or not flow["independent_effects"]:
        score = min(score, HIGH_CONFIDENCE - 0.01)
    return {
        "name": facts.name,
        "line": facts.line,
        "kind": "callable",
        "coefficient": round(score, 12),
        "metrics": asdict(facts),
        "signals": {**signals, "mixed_effects": mixed},
        "effect_domains": domains,
        "direct_effect_domains": direct,
        "delegated_effect_domains": delegated,
        "effect_flow": flow,
        "counterevidence": ["effect groups share a data-flow workflow"]
        if flow["shared_workflow"]
        else [],
        "reasons": [
            f"{name} operations via resolved helpers"
            if name in delegated
            else f"direct {name} operations"
            for name in strong_domains
        ]
        + [f"{name}={value:.2f}" for name, value in signals.items() if value],
    }
