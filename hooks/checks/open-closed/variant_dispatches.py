import ast
import sys
from pathlib import Path

from central_constructions import CentralConstructions
from closed_factories import closed_factories
from concrete_type_comparisons import ConcreteTypeComparisons
from module_constants import string_constants
from ocp_findings import (
    FUNCTION_NODES,
    CentralConstruction,
    ClosedFactory,
    ConcreteFactoryDependency,
    ClosedVisitor,
    FragmentedRegistry,
    RegistryEscape,
    ConcreteTypeDispatch,
    Finding,
    ScatteredVariantDispatch,
    VariantDispatch,
)
from python_structures import structural_findings
from scattered_comparisons import scattered_comparisons, top_level_scopes
from string_comparisons import StringComparisons


class VariantDispatches:
    def find_in(self, paths: list[str]) -> list[Finding]:
        found: list[Finding] = [*structural_findings(paths)]

        for path in paths:
            found.extend(self._find_in_file(Path(path)))

        return sorted(found)

    def _find_in_file(self, path: Path) -> list[Finding]:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        constants = string_constants(tree)
        found: list[Finding] = [*closed_factories(str(path), tree)]
        found.extend(
            scattered_comparisons(
                str(path), top_level_scopes(tree), constants
            )
        )

        for scope in ast.walk(tree):
            if not isinstance(scope, FUNCTION_NODES):
                continue

            collector = StringComparisons(scope, constants)
            collector.visit(scope)
            type_collector = ConcreteTypeComparisons(scope)
            type_collector.visit(scope)
            construction_collector = CentralConstructions(scope)
            construction_collector.visit(scope)
            name = getattr(scope, "name", "(anonymous)")
            constructions = construction_collector.collected()
            constructed_subjects = {key for key, _, _ in constructions}

            for key, subject, variants in collector.collected():
                if key not in constructed_subjects:
                    found.append(
                        VariantDispatch(
                            str(path), scope.lineno, name, subject, variants
                        )
                    )

            for subject, concrete_types in type_collector.collected():
                found.append(
                    ConcreteTypeDispatch(
                        str(path), scope.lineno, name, subject, concrete_types
                    )
                )

            for _, subject, implementations in constructions:
                found.append(
                    CentralConstruction(
                        str(path), scope.lineno, name, subject, implementations
                    )
                )

        return found


def message_for(dispatch: Finding) -> str:
    if isinstance(dispatch, VariantDispatch):
        values = ", ".join(dispatch.variants)
        return (
            f"{dispatch.function_name} compares {dispatch.subject} to "
            f"{len(dispatch.variants)} strings: {values}"
        )
    if isinstance(dispatch, ConcreteTypeDispatch):
        values = ", ".join(dispatch.concrete_types)
        return (
            f"{dispatch.function_name} dispatches {dispatch.subject} across "
            f"{len(dispatch.concrete_types)} concrete types: {values}"
        )
    if isinstance(dispatch, ScatteredVariantDispatch):
        values = ", ".join(dispatch.variants)
        return (
            f"{dispatch.subject} dispatch is scattered across "
            f"{dispatch.function_count} functions, starting at "
            f"{dispatch.function_name}: {values}"
        )
    if isinstance(dispatch, ClosedFactory):
        values = ", ".join(dispatch.implementations)
        return (
            f"{dispatch.function_name} closes {dispatch.abstraction} over "
            f"concrete implementations: {values}"
        )
    if isinstance(dispatch, ConcreteFactoryDependency):
        values = ", ".join(dispatch.dependencies)
        return (
            f"{dispatch.factory_name} leaks concrete dependencies while "
            f"creating {dispatch.abstraction}: {values}"
        )
    if isinstance(dispatch, RegistryEscape):
        return (
            f"{dispatch.function_name} branches on {dispatch.axis} outside "
            f"its handler registry in {', '.join(dispatch.registry_paths)}"
        )
    if isinstance(dispatch, FragmentedRegistry):
        return (
            f"{dispatch.axis} behavior is split across "
            f"{len(dispatch.registry_names)} registries in "
            f"{dispatch.file_count} "
            f"{'file' if dispatch.file_count == 1 else 'files'}: "
            f"{', '.join(dispatch.registry_names)}"
        )
    if isinstance(dispatch, ClosedVisitor):
        return (
            f"{dispatch.visitor_name} requires one callback for every "
            f"{dispatch.axis} variant: {', '.join(dispatch.variants)}"
        )

    values = ", ".join(dispatch.implementations)
    return (
        f"{dispatch.function_name} centrally constructs "
        f"{len(dispatch.implementations)} implementations selected by "
        f"{dispatch.subject}: {values}"
    )


def main() -> None:
    source_paths = sys.stdin.read().split()

    for dispatch in VariantDispatches().find_in(source_paths):
        _ = sys.stdout.write(
            f"{dispatch.path}:{dispatch.line_number}: "
            f"{message_for(dispatch)}\n"
        )


if __name__ == "__main__":
    main()
