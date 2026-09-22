from srp_effect_rules import EFFECT_RULES


def effect_domains(calls: list[str]) -> dict[str, list[str]]:
    domains: dict[str, set[str]] = {}
    for call in calls:
        for domain, prefixes, operations in EFFECT_RULES:
            if call.rsplit(".", 1)[-1] not in operations:
                continue
            if any(call == p or call.startswith(p + ".") for p in prefixes):
                domains.setdefault(domain, set()).add(call)
    return {name: sorted(found) for name, found in sorted(domains.items())}
