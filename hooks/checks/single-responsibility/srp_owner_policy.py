"""Combine distinct evidence families, not several versions of cohesion."""

from srp_clients import client_evidence
from srp_metrics import HIGH_CONFIDENCE, ramp


def owner_coefficient(
    owner: dict,
    metrics: dict,
    structural: float,
    separation: float,
    support: float,
    clients: dict,
) -> dict:
    component_groups = metrics["supported_groups"]
    effect_groups = list(metrics["effect_groups"].values())
    component_clients = client_evidence(
        owner.get("path", ""), component_groups, clients
    )
    effect_clients = client_evidence(owner.get("path", ""), effect_groups, clients)
    evidence = []
    counterevidence = []
    score = 0.10 * structural
    if metrics["normalized_components"] is not None:
        score += 0.40 * separation + 0.15 * support
    if len(component_groups) >= 2:
        evidence.append("supported independent member groups")
    if len(effect_groups) >= 2:
        evidence.append("separate I/O implementations")
        score = max(
            score,
            0.50 + 0.15 * (1 - metrics["external_similarity"]) + 0.10 * structural,
        )
    if component_clients["shared_clients"] or effect_clients["shared_clients"]:
        counterevidence.append("observed callers use multiple groups together")
        score = max(0.0, score - 0.05)
    if component_clients["segregated"] or effect_clients["segregated"]:
        evidence.append("separate client populations corroborate the partition")
        score = max(score, HIGH_CONFIDENCE + 0.10 * structural)
    # PMD/Marinescu-inspired conjunction. These runtime metrics are proxies,
    # not a port of PMD's Java type-resolved metrics or a proof of SRP.
    tight = metrics["tight_cohesion"]
    god_class = (
        owner["kind"] == "class"
        and tight is not None
        and tight < 1 / 3
        and metrics["weighted_methods"] >= 47
        and metrics["foreign_data"] > 5
    )
    if god_class:
        evidence.append("high complexity, foreign-data access and low field cohesion")
        score = max(
            score,
            HIGH_CONFIDENCE
            + 0.10 * ramp(metrics["weighted_methods"], 47, 100)
            + 0.10 * (1 - tight),
        )
    return {
        "coefficient": round(min(1.0, score), 12),
        "evidence": evidence,
        "counterevidence": counterevidence,
        "client_usage": {"components": component_clients, "effects": effect_clients},
        "god_class_risk": god_class,
    }
