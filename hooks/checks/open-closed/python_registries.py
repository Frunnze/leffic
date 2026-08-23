import ast

from ocp_findings import FragmentedRegistry
from python_registry_domains import contains_behavior, registry_domain
from python_structure_types import (
    Axis,
    Module,
    Registry,
    assigned_name,
    axis_for_domain,
    mapping_axis,
)


def registries_in(
    modules: list[Module], axes: dict[str, list[Axis]]
) -> list[Registry]:
    found: list[Registry] = []

    for module in modules:
        for node in module.tree.body:
            if not isinstance(node, (ast.Assign, ast.AnnAssign)):
                continue

            name = assigned_name(node)
            value = node.value

            if name is None or value is None:
                continue

            explicit_axis = (
                mapping_axis(node.annotation, axes)
                if isinstance(node, ast.AnnAssign)
                else None
            )
            domain = registry_domain(value, module.constants)

            if explicit_axis is not None:
                domain = set(explicit_axis.domain)
            if domain is None or len(domain) < 2:
                continue

            axis = explicit_axis or axis_for_domain(domain, axes)
            found.append(
                Registry(
                    module.path,
                    node.lineno,
                    name,
                    axis or Axis("variant", frozenset(domain)),
                    contains_behavior(value, module.constants),
                )
            )

    return found


def fragmented_registries(
    registries: list[Registry],
) -> list[FragmentedRegistry]:
    groups: dict[frozenset[str], list[Registry]] = {}

    for registry in registries:
        groups.setdefault(registry.axis.domain, []).append(registry)

    found: list[FragmentedRegistry] = []

    for group in groups.values():
        enough = len(group) >= 3 or (
            len(group) >= 2 and len(group[0].axis.domain) >= 3
        )

        if not enough:
            continue

        ordered = sorted(group, key=lambda item: (item.path, item.line_number))
        first = ordered[0]
        labels = sorted(
            {item.axis.name for item in group if item.axis.name != "variant"}
        )
        found.append(
            FragmentedRegistry(
                first.path,
                first.line_number,
                labels[0] if labels else "variant",
                tuple(sorted(item.name for item in group)),
                len({item.path for item in group}),
            )
        )

    return found
