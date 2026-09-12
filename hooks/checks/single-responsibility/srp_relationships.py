"""Research-informed cohesion diagnostics; variants are explicitly labelled."""

from itertools import combinations

from srp_effects import effect_domains
from srp_metrics import CallableFacts


def transitive_resources(members: list[CallableFacts]) -> list[set[str]]:
    resources = [set(member.resources) for member in members]
    indices = {member.name: index for index, member in enumerate(members)}
    changed = True
    while changed:
        changed = False
        for index, member in enumerate(members):
            before = len(resources[index])
            for name in member.links:
                if name in indices:
                    resources[index].update(resources[indices[name]])
            changed |= before != len(resources[index])
    return resources


def pair_cohesion(members: list[CallableFacts], groups: list[list[int]]) -> dict:
    resources = transitive_resources(members)
    field_sets = [
        {value for value in values if value.startswith("field:")}
        for values in resources
    ]
    pairs = list(combinations(range(len(members)), 2))
    measurable = bool(pairs) and any(field_sets)
    member_names = {member.name for member in members}
    linked = any(
        set(member.links) & (member_names - {member.name}) for member in members
    )
    direct = sum(bool(field_sets[a] & field_sets[b]) for a, b in pairs)
    adjacency = [set() for _ in members]
    for a, b in pairs:
        if field_sets[a] & field_sets[b]:
            adjacency[a].add(b)
            adjacency[b].add(a)
    connected_pairs = 0
    for start in range(len(members)):
        seen, pending = {start}, [start]
        while pending:
            for other in adjacency[pending.pop()] - seen:
                seen.add(other)
                pending.append(other)
        connected_pairs += sum(other > start for other in seen)
    return {
        # Runtime-member variants: include private helpers; omit constructors.
        "tight_cohesion": direct / len(pairs) if measurable else None,
        "loose_cohesion": connected_pairs / len(pairs) if measurable else None,
        "normalized_components": (
            len(groups) / len(members) if len(groups) > 1 else 0.0
        )
        if members and (any(resources) or linked)
        else None,
    }


def external_profiles(members: list[CallableFacts]) -> dict:
    """Separate effects even when every method also reads common entity data."""
    domains = [
        effect_domains(member.calls + member.delegated_effects) for member in members
    ]
    profiles = [set(profile) for profile in domains]
    active = [i for i, profile in enumerate(profiles) if profile]
    pairs = list(combinations(active, 2))
    similarities = [
        len(profiles[a] & profiles[b]) / len(profiles[a] | profiles[b])
        for a, b in pairs
    ]
    groups: dict[str, list[int]] = {}
    for index in active:
        if len(profiles[index]) == 1 and members[index].statements >= 2:
            domain = next(iter(profiles[index]))
            groups.setdefault(domain, []).append(index)
    supported: dict[str, list[str]] = {}
    for domain, indices in sorted(groups.items()):
        operations = {call for index in indices for call in domains[index][domain]}
        if (
            len(indices) >= 2
            and len(operations) >= 2
            and sum(members[i].statements for i in indices) >= 12
        ):
            supported[domain] = [members[i].name for i in indices]
    return {
        "external_similarity": sum(similarities) / len(similarities)
        if similarities
        else None,
        "effect_groups": supported,
    }
