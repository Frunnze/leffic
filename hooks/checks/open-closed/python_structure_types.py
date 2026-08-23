import ast
from dataclasses import dataclass
from pathlib import Path

from module_constants import string_constants

_MAPPING_NAMES = {"dict", "Dict", "Mapping", "MutableMapping"}


@dataclass(frozen=True)
class Axis:
    name: str
    domain: frozenset[str]


@dataclass(frozen=True)
class Registry:
    path: str
    line_number: int
    name: str
    axis: Axis
    is_behavior: bool


@dataclass(frozen=True)
class Module:
    path: str
    tree: ast.Module
    constants: dict[str, str]


def modules_from(paths: list[str]) -> list[Module]:
    return [
        Module(
            path,
            tree := ast.parse(Path(path).read_text(encoding="utf-8")),
            string_constants(tree),
        )
        for path in paths
    ]


def _add_axis(
    found: dict[str, list[Axis]], name: str, domain: set[str]
) -> None:
    if len(domain) < 2:
        return

    axis = Axis(name, frozenset(domain))
    if axis not in found.setdefault(name, []):
        found[name].append(axis)


def axes_in(modules: list[Module]) -> dict[str, list[Axis]]:
    found: dict[str, list[Axis]] = {}

    for module in modules:
        for node in module.tree.body:
            if isinstance(node, (ast.Assign, ast.AnnAssign)):
                name = assigned_name(node)
                value = node.value

                if name is not None and value is not None:
                    domain = literal_annotation(value)

                    if domain is not None:
                        _add_axis(found, name, domain)
            elif isinstance(node, ast.ClassDef) and inherits_from(
                node, {"Enum", "StrEnum"}
            ):
                values = {
                    value
                    for member in node.body
                    if isinstance(member, (ast.Assign, ast.AnnAssign))
                    if (value := string_value(member.value, module.constants))
                    is not None
                }
                _add_axis(found, node.name, values)

    return found


def literal_annotation(node: ast.AST) -> set[str] | None:
    if not isinstance(node, ast.Subscript):
        return None
    if expression_name(node.value).rsplit(".", 1)[-1] != "Literal":
        return None

    values = node.slice.elts if isinstance(node.slice, ast.Tuple) else [node.slice]
    domain = {
        value.value
        for value in values
        if isinstance(value, ast.Constant) and isinstance(value.value, str)
    }

    return domain if len(domain) == len(values) else None


def class_fields(
    modules: list[Module], axes: dict[str, list[Axis]]
) -> dict[tuple[str, str], Axis]:
    fields: dict[tuple[str, str], Axis] = {}

    for module in modules:
        for owner in (
            node for node in module.tree.body if isinstance(node, ast.ClassDef)
        ):
            for member in owner.body:
                if not isinstance(member, ast.AnnAssign):
                    continue
                if not isinstance(member.target, ast.Name):
                    continue

                axis = axis_from_annotation(member.annotation, axes)

                if axis is not None:
                    fields[(owner.name, member.target.id)] = axis

    return fields


def mapping_axis(
    annotation: ast.AST, axes: dict[str, list[Axis]]
) -> Axis | None:
    if not isinstance(annotation, ast.Subscript):
        return None
    if expression_name(annotation.value).rsplit(".", 1)[-1] not in _MAPPING_NAMES:
        return None

    arguments = (
        annotation.slice.elts
        if isinstance(annotation.slice, ast.Tuple)
        else [annotation.slice]
    )

    return axis_from_annotation(arguments[0], axes)


def axis_from_annotation(
    annotation: ast.AST, axes: dict[str, list[Axis]]
) -> Axis | None:
    domain = literal_annotation(annotation)

    if domain is not None:
        return Axis("Literal", frozenset(domain))

    name = expression_name(annotation).rsplit(".", 1)[-1]
    candidates = axes.get(name, [])

    return candidates[0] if len(candidates) == 1 else None


def axis_for_domain(
    domain: set[str], axes: dict[str, list[Axis]]
) -> Axis | None:
    matches = [
        axis
        for candidates in axes.values()
        for axis in candidates
        if axis.domain == frozenset(domain)
    ]

    return min(matches, key=lambda axis: axis.name) if matches else None


def assigned_name(node: ast.Assign | ast.AnnAssign) -> str | None:
    if isinstance(node, ast.AnnAssign):
        return node.target.id if isinstance(node.target, ast.Name) else None
    if len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name):
        return None

    return node.targets[0].id


def string_value(
    node: ast.AST | None, constants: dict[str, str]
) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.Name):
        return constants.get(node.id)

    return None


def inherits_from(owner: ast.ClassDef, names: set[str]) -> bool:
    return any(
        expression_name(base).rsplit(".", 1)[-1] in names
        for base in owner.bases
    )


def expression_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        owner = expression_name(node.value)
        return f"{owner}.{node.attr}" if owner else node.attr

    return ""
