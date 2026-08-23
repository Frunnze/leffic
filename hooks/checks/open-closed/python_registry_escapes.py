import ast

from ocp_findings import RegistryEscape
from python_structure_types import (
    Axis,
    Module,
    Registry,
    axis_from_annotation,
    expression_name,
    string_value,
)


def registry_escapes(
    modules: list[Module],
    axes: dict[str, list[Axis]],
    fields: dict[tuple[str, str], Axis],
    registries: list[Registry],
) -> list[RegistryEscape]:
    behavior = [registry for registry in registries if registry.is_behavior]
    found: list[RegistryEscape] = []

    for module in modules:
        for scope in ast.walk(module.tree):
            if not isinstance(scope, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue

            parameters = {
                argument.arg: _axis_or_owner(argument.annotation, axes)
                for argument in [*scope.args.posonlyargs, *scope.args.args]
                if argument.annotation is not None
            }
            found.extend(
                _escapes_in_scope(
                    module, scope, parameters, fields, behavior
                )
            )

    return found


def _escapes_in_scope(
    module: Module,
    scope: ast.FunctionDef | ast.AsyncFunctionDef,
    parameters: dict[str, Axis | str | None],
    fields: dict[tuple[str, str], Axis],
    behavior: list[Registry],
) -> list[RegistryEscape]:
    found: list[RegistryEscape] = []
    seen: set[tuple[str, tuple[str, ...]]] = set()

    for comparison in (
        node for node in ast.walk(scope) if isinstance(node, ast.Compare)
    ):
        subject = _comparison_subject(comparison, module.constants)

        if subject is None:
            continue

        axis = _subject_axis(subject, parameters, fields)

        if axis is None:
            continue

        matching = [
            registry
            for registry in behavior
            if axis.domain <= registry.axis.domain
            and registry.path != module.path
        ]

        if not matching:
            continue

        paths = tuple(sorted({registry.path for registry in matching}))
        key = (axis.name, paths)

        if key in seen:
            continue

        seen.add(key)
        found.append(
            RegistryEscape(
                module.path,
                scope.lineno,
                scope.name,
                axis.name,
                paths,
            )
        )

    return found


def _axis_or_owner(
    annotation: ast.AST, axes: dict[str, list[Axis]]
) -> Axis | str | None:
    axis = axis_from_annotation(annotation, axes)

    return axis or expression_name(annotation).rsplit(".", 1)[-1]


def _comparison_subject(
    comparison: ast.Compare, constants: dict[str, str]
) -> ast.AST | None:
    if len(comparison.ops) != 1 or len(comparison.comparators) != 1:
        return None
    if not isinstance(comparison.ops[0], (ast.Eq, ast.NotEq, ast.Is, ast.IsNot)):
        return None

    left = comparison.left
    right = comparison.comparators[0]

    if string_value(left, constants) is not None:
        return right
    if string_value(right, constants) is not None:
        return left

    return None


def _subject_axis(
    subject: ast.AST,
    parameters: dict[str, Axis | str | None],
    fields: dict[tuple[str, str], Axis],
) -> Axis | None:
    if isinstance(subject, ast.Name):
        value = parameters.get(subject.id)

        return value if isinstance(value, Axis) else None
    if isinstance(subject, ast.Attribute) and isinstance(subject.value, ast.Name):
        owner = parameters.get(subject.value.id)

        if isinstance(owner, str):
            return fields.get((owner, subject.attr))

    return None
