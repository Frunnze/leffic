import ast

from factory_dependencies import abstract_classes, constructed_dependencies
from ocp_findings import ClosedFactory, ConcreteFactoryDependency

_FACTORY_VERBS = ("build", "create", "get", "make", "resolve")


def closed_factories(
    path: str, tree: ast.Module
) -> list[ClosedFactory | ConcreteFactoryDependency]:
    bases = _class_bases(tree)
    abstractions_in_module = abstract_classes(tree)
    found: list[ClosedFactory | ConcreteFactoryDependency] = []

    for owner in (node for node in tree.body if isinstance(node, ast.ClassDef)):
        abstractions: set[str] = set()

        for method in owner.body:
            if not isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if not _is_factory_method(owner.name, method.name):
                continue

            abstraction = _annotation_name(method.returns)

            if abstraction is None:
                continue

            if abstraction in abstractions_in_module:
                abstractions.add(abstraction)

            implementations = tuple(
                sorted(
                    concrete
                    for concrete in _returned_constructors(method)
                    if concrete != abstraction
                    and _inherits(concrete, abstraction, bases)
                )
            )

            if implementations:
                found.append(
                    ClosedFactory(
                        path,
                        method.lineno,
                        method.name,
                        abstraction,
                        implementations,
                    )
                )

        constructor = next(
            (
                method
                for method in owner.body
                if isinstance(method, ast.FunctionDef)
                and method.name == "__init__"
            ),
            None,
        )

        if constructor is not None and abstractions:
            dependencies = constructed_dependencies(constructor)

            if dependencies:
                found.append(
                    ConcreteFactoryDependency(
                        path,
                        constructor.lineno,
                        owner.name,
                        ", ".join(sorted(abstractions)),
                        tuple(sorted(dependencies)),
                    )
                )

    return sorted(found)


def _class_bases(tree: ast.Module) -> dict[str, set[str]]:
    return {
        node.name: {
            name
            for base in node.bases
            if (name := _expression_name(base)) is not None
        }
        for node in tree.body
        if isinstance(node, ast.ClassDef)
    }


def _is_factory_method(owner: str, method: str) -> bool:
    if method.startswith("_"):
        return False

    return owner.casefold().endswith("factory") or method.startswith(
        _FACTORY_VERBS
    )


def _annotation_name(annotation: ast.expr | None) -> str | None:
    if not isinstance(annotation, (ast.Name, ast.Attribute)):
        return None

    return _expression_name(annotation)


def _returned_constructors(scope: ast.AST) -> set[str]:
    found: set[str] = set()

    for node in ast.walk(scope):
        if not isinstance(node, ast.Return) or not isinstance(node.value, ast.Call):
            continue

        name = _expression_name(node.value.func)

        if name is not None and name.rsplit(".", 1)[-1][:1].isupper():
            found.add(name.rsplit(".", 1)[-1])

    return found


def _inherits(
    concrete: str, abstraction: str, bases: dict[str, set[str]]
) -> bool:
    pending = [concrete]
    visited: set[str] = set()

    while pending:
        current = pending.pop()

        if current in visited:
            continue

        visited.add(current)
        direct = bases.get(current, set())

        if abstraction in direct:
            return True

        pending.extend(direct)

    return False


def _expression_name(node: ast.expr) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        owner = _expression_name(node.value)
        return node.attr if owner is None else f"{owner}.{node.attr}"

    return None
