import ast
import sys
from pathlib import Path
from typing import NamedTuple

MAXIMUM_METHODS = 4
FUNCTION_NODES = (ast.FunctionDef, ast.AsyncFunctionDef)
PINNED_METHOD_COUNTS: dict[str, int] = {}


class CrowdedClass(NamedTuple):
    path: str
    line_number: int
    name: str
    method_count: int


class CrowdedClasses:
    def find_in(self, paths: list[str]) -> list[CrowdedClass]:
        found: list[CrowdedClass] = []

        for path in paths:
            found.extend(self._find_in_file(Path(path)))

        return sorted(found)

    def _find_in_file(self, path: Path) -> list[CrowdedClass]:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        found: list[CrowdedClass] = []

        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue

            method_count = self._count_methods(node)

            if method_count > self._allowed_for(path, node.name):
                found.append(
                    CrowdedClass(
                        str(path), node.lineno, node.name, method_count
                    )
                )

        return found

    def _allowed_for(self, path: Path, class_name: str) -> int:
        return PINNED_METHOD_COUNTS.get(
            f"{path}::{class_name}", MAXIMUM_METHODS
        )

    def _count_methods(self, node: ast.ClassDef) -> int:
        method_count = 0

        for child in node.body:
            if isinstance(child, FUNCTION_NODES):
                method_count += 1

        return method_count


source_paths = sys.stdin.read().split()

for crowded in CrowdedClasses().find_in(source_paths):
    summary = f"{crowded.name} has {crowded.method_count} methods"
    _ = sys.stdout.write(
        f"{crowded.path}:{crowded.line_number}: {summary}\n"
    )
