"""Cohesion through shared state/dependencies and direct member calls."""

from srp_metrics import CallableFacts, burden, implementation_burden
from srp_owner_policy import owner_coefficient
from srp_relationships import external_profiles, pair_cohesion


def components(members: list[CallableFacts]) -> list[list[int]]:
    remaining = set(range(len(members)))
    groups: list[list[int]] = []
    resources = [set(member.resources) for member in members]
    while remaining:
        group = {min(remaining)}
        pending = list(group)
        remaining.difference_update(group)
        while pending:
            current = pending.pop()
            for other in sorted(remaining):
                connected = (
                    resources[current] & resources[other]
                    or members[other].name in members[current].links
                    or members[current].name in members[other].links
                )
                if connected:
                    group.add(other)
                    pending.append(other)
                    remaining.remove(other)
        groups.append(sorted(group))
    return groups


def owner_score(
    owner: dict, callables: list[CallableFacts], clients: dict | None = None
) -> dict:
    members = [
        member
        for member in callables
        if member.owner == owner["name"]
        and member.name.rsplit(".", 1)[-1] not in {"__init__", "__new__", "constructor"}
        and member.statements >= 1
    ]
    groups = components(members)
    supported = [
        group
        for group in groups
        if sum(members[i].statements >= 2 for i in group) >= 2
        and sum(members[i].statements for i in group) >= 6
        and (
            any(members[i].resources for i in group)
            or any(
                members[j].name in members[i].links
                for i in group
                for j in group
                if i != j
            )
        )
    ]
    count = len(members)
    disconnected = (1 - max(map(len, groups)) / count) if count else 0.0
    support = min(
        (sum(members[i].statements for i in group) / 12 for group in supported),
        default=0,
    )
    structural = max(
        (implementation_burden(burden(member)) for member in members), default=0
    )
    if len(supported) < 2:
        support = 0.0
    relationships = pair_cohesion(members, groups)
    profiles = external_profiles(members)
    effect_groups = profiles["effect_groups"]
    group_names = [[members[i].name for i in group] for group in groups]
    metrics = {
        "members": count,
        "components": len(groups),
        "supported_components": len(supported),
        "groups": group_names,
        "supported_groups": [[members[i].name for i in group] for group in supported],
        "weighted_methods": sum(member.complexity for member in members),
        "foreign_data": len(
            {name for member in members for name in member.foreign_data}
        ),
        **relationships,
        **profiles,
    }
    decision = owner_coefficient(
        owner,
        metrics,
        structural,
        min(1.0, 2 * disconnected),
        min(1.0, support),
        clients or {},
    )
    return {
        **owner,
        **decision,
        "metrics": metrics,
        "signals": {
            "disconnected_fraction": disconnected,
            "group_support": min(1.0, support),
            "implementation_burden": structural,
        },
        "reasons": decision["evidence"]
        + decision["counterevidence"]
        + (
            [
                "independent member groups: "
                + " | ".join(
                    ", ".join(members[i].name for i in group) for group in supported
                )
            ]
            if len(supported) >= 2
            else []
        )
        + (
            [
                "separate I/O implementations: "
                + " | ".join(
                    f"{domain}: {', '.join(names)}"
                    for domain, names in effect_groups.items()
                )
            ]
            if len(effect_groups) >= 2
            else []
        ),
    }
