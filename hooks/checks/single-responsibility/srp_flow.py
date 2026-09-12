"""Effect-slice overlap can refute an apparent collection of separate jobs."""

from itertools import combinations

from srp_effects import effect_domains


def effect_flow(blocks: list[dict]) -> dict:
    definitions: dict[str, set[int]] = {}
    slices: dict[str, set[int]] = {}
    operations: dict[str, set[str]] = {}
    events: dict[str, set[int]] = {}
    for index, block in enumerate(blocks):
        dependencies = {index}
        for name in block["reads"]:
            dependencies.update(definitions.get(name, set()))
        for name in block["writes"]:
            previous = definitions.get(name, set()) if block["compound"] else set()
            definitions[name] = dependencies | previous
        for domain, calls in effect_domains(
            block["calls"] + block.get("delegated_effects", [])
        ).items():
            slices.setdefault(domain, set()).update(dependencies)
            operations.setdefault(domain, set()).update(calls)
            events.setdefault(domain, set()).add(index)
    strong = sorted(
        domain
        for domain in slices
        if len(operations[domain]) >= 2 and len(slices[domain]) >= 4
    )
    adjacency = {domain: set() for domain in strong}
    overlaps = []
    for left, right in combinations(strong, 2):
        overlap = len(slices[left] & slices[right]) / min(
            len(slices[left]), len(slices[right])
        )
        linked = bool(events[left] & slices[right] or events[right] & slices[left])
        overlaps.append(
            {"left": left, "right": right, "overlap": overlap, "data_flow": linked}
        )
        if linked or overlap >= 0.5:
            adjacency[left].add(right)
            adjacency[right].add(left)
    remaining, groups = set(strong), []
    while remaining:
        pending, group = [min(remaining)], set()
        while pending:
            domain = pending.pop()
            if domain in group:
                continue
            group.add(domain)
            pending.extend(adjacency[domain] - group)
        remaining.difference_update(group)
        groups.append(sorted(group))
    return {
        "status": "observed" if len(strong) >= 2 else "insufficient_evidence",
        "groups": groups,
        "independent_effects": len(groups) >= 2,
        "shared_workflow": len(strong) >= 2 and len(groups) == 1,
        "pairs": overlaps,
        "slice_lines": {
            domain: sorted({blocks[i]["line"] for i in indices})
            for domain, indices in sorted(slices.items())
        },
    }
