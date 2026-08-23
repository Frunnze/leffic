import ast

from ocp_findings import ClosedVisitor
from python_structure_types import Axis, Module, inherits_from

_VISITOR_BASES = {"ABC", "Protocol", "TypedDict"}


def closed_visitors(
    modules: list[Module], axes: dict[str, list[Axis]]
) -> list[ClosedVisitor]:
    found: list[ClosedVisitor] = []
    all_axes = [axis for candidates in axes.values() for axis in candidates]

    for module in modules:
        for owner in (
            node for node in module.tree.body if isinstance(node, ast.ClassDef)
        ):
            if not inherits_from(owner, _VISITOR_BASES):
                continue

            callbacks = _callbacks_of(owner)

            for axis in all_axes:
                if len(axis.domain) < 3:
                    continue
                if not _callbacks_close(callbacks, axis.domain):
                    continue

                found.append(
                    ClosedVisitor(
                        module.path,
                        owner.lineno,
                        owner.name,
                        axis.name,
                        tuple(sorted(axis.domain)),
                    )
                )
                break

    return found


def _callbacks_of(owner: ast.ClassDef) -> set[str]:
    callbacks = {
        member.name
        for member in owner.body
        if isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef))
        and not member.name.startswith("_")
    }
    callbacks.update(
        member.target.id
        for member in owner.body
        if isinstance(member, ast.AnnAssign)
        and isinstance(member.target, ast.Name)
        and "Callable" in ast.unparse(member.annotation)
    )

    return callbacks


def _callbacks_close(
    callbacks: set[str], domain: frozenset[str]
) -> bool:
    if callbacks == domain:
        return True

    for callback in callbacks:
        for variant in domain:
            if not callback.endswith(variant):
                continue

            prefix = callback[: -len(variant)]

            if callbacks == {f"{prefix}{value}" for value in domain}:
                return True

    return False
