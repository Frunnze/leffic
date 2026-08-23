import ast
from collections.abc import Iterator

from ocp_findings import EQUALITY_NODES, FUNCTION_NODES, MAXIMUM_VARIANTS
from scoped_visitor import ScopedVisitor


class CentralConstructions(ScopedVisitor):
    def __init__(self, root: ast.AST) -> None:
        super().__init__(root)
        self._subjects: dict[str, tuple[str, set[str], set[str]]] = {}

    def collected(self) -> list[tuple[str, str, tuple[str, ...]]]:
        found: list[tuple[str, str, tuple[str, ...]]] = []

        for key, (subject, variants, implementations) in self._subjects.items():
            if (
                len(variants) > MAXIMUM_VARIANTS
                and len(implementations) > MAXIMUM_VARIANTS
            ):
                found.append((key, subject, tuple(sorted(implementations))))

        return sorted(found)

    def visit_If(self, node: ast.If) -> None:
        for comparison in ast.walk(node.test):
            if not isinstance(comparison, ast.Compare):
                continue

            selected = self._string_comparison(comparison)

            if selected is not None:
                subject, variant = selected
                self._record(subject, variant, node.body)

        self.generic_visit(node)

    def visit_Match(self, node: ast.Match) -> None:
        for match_case in node.cases:
            variants = []

            for pattern in ast.walk(match_case.pattern):
                if not isinstance(pattern, ast.MatchValue):
                    continue
                if (
                    isinstance(pattern.value, ast.Constant)
                    and isinstance(pattern.value.value, str)
                ):
                    variants.append(pattern.value.value)

            for variant in variants:
                self._record(node.subject, variant, match_case.body)

        self.generic_visit(node)

    def _string_comparison(
        self, node: ast.Compare
    ) -> tuple[ast.expr, str] | None:
        if len(node.ops) != 1 or not isinstance(node.ops[0], EQUALITY_NODES):
            return None

        left = node.left
        right = node.comparators[0]

        if isinstance(left, ast.Constant) and isinstance(left.value, str):
            return right, left.value
        if isinstance(right, ast.Constant) and isinstance(right.value, str):
            return left, right.value

        return None

    def _record(
        self, subject: ast.expr, variant: str, body: list[ast.stmt]
    ) -> None:
        implementations = self._constructors_in(body)

        if not implementations:
            return

        key = ast.dump(subject, include_attributes=False)
        display, variants, selected = self._subjects.setdefault(
            key, (ast.unparse(subject), set(), set())
        )
        variants.add(variant)
        selected.update(implementations)
        self._subjects[key] = (display, variants, selected)

    def _constructors_in(self, body: list[ast.stmt]) -> set[str]:
        found: set[str] = set()

        for statement in body:
            for node in self._walk_without_nested_scopes(statement):
                if not isinstance(node, ast.Call):
                    continue

                name = self._constructor_name(node.func)

                if name is not None:
                    found.add(name)

        return found

    def _walk_without_nested_scopes(self, root: ast.AST) -> Iterator[ast.AST]:
        pending = [root]

        while pending:
            node = pending.pop()
            yield node

            nested_scope = (*FUNCTION_NODES, ast.ClassDef)
            if node is not root and isinstance(node, nested_scope):
                continue

            pending.extend(ast.iter_child_nodes(node))

    def _constructor_name(self, node: ast.expr) -> str | None:
        if not isinstance(node, (ast.Name, ast.Attribute)):
            return None

        name = ast.unparse(node)
        terminal = name.rsplit(".", 1)[-1]

        return name if terminal[:1].isupper() else None
