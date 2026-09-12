"""Resolve observed callers within each source tree; absence is unknown."""

from itertools import combinations

from srp_imports import ImportResolver


def caller_index(parsed: list[dict]) -> dict[tuple[str, str], set[str]]:
    resolver = ImportResolver(parsed)
    symbols = resolver.symbols
    clients = {(path, name): set() for path, names in symbols.items() for name in names}
    edges: dict[tuple[str, str], set[tuple[str, str]]] = {}
    for item in parsed:
        path = item["path"]
        for fact in item["facts"]:
            caller = (path, fact.name)
            targets = {(path, name) for name in fact.links if name in symbols[path]}
            for call in set(fact.calls + fact.references):
                targets.update(resolver.resolve(path, call))
            edges[caller] = targets
            for target in targets:
                if target[0] != path:
                    clients[target].add(path)
    # Carry observed external clients through internal helpers and wrappers.
    changed = True
    while changed:
        changed = False
        for caller, targets in edges.items():
            for target in targets:
                before = len(clients[target])
                clients[target].update(
                    client for client in clients[caller] if client != target[0]
                )
                changed |= before != len(clients[target])
    return clients


def client_evidence(path: str, groups: list[list[str]], clients: dict) -> dict:
    observed = [
        set().union(*(clients.get((path, name), set()) for name in group))
        for group in groups
    ]
    pairs = list(combinations(observed, 2))
    shared = set().union(*(left & right for left, right in pairs))
    measured = bool(pairs) and all(observed)
    similarities = [
        len(left & right) / len(left | right) for left, right in pairs if left | right
    ]
    return {
        "groups": [sorted(group) for group in observed],
        "similarity": sum(similarities) / len(similarities) if measured else None,
        "shared_clients": sorted(shared),
        "segregated": measured
        and not shared
        and all(len(group) >= 2 for group in observed),
        "status": "observed" if measured else "insufficient_evidence",
    }
