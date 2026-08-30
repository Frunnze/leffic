import ast

from tests.migration_support import service_root

_BOOTSTRAP_NAME = "create_postgres_database_if_configured"
_DATABASE_MODULE = "shared.database"
_SET_MAIN_OPTION = "set_main_option"
_GET_MAIN_OPTION = "get_main_option"


def _environment_tree() -> ast.Module:
    source = (service_root() / "migrations" / "env.py").read_text(
        encoding="utf-8"
    )

    return ast.parse(source)


def names_imported_from_the_database_module() -> set[str]:
    imported: set[str] = set()

    for node in ast.walk(_environment_tree()):
        if not isinstance(node, ast.ImportFrom):
            continue

        if node.module != _DATABASE_MODULE:
            continue

        for alias in node.names:
            imported.add(alias.name)

    return imported


def _called_name(call: ast.Call) -> str:
    if isinstance(call.func, ast.Name):
        return call.func.id

    if isinstance(call.func, ast.Attribute):
        return call.func.attr

    return ""


def _call_lines(node: ast.AST, called_name: str) -> list[int]:
    lines: list[int] = []

    for child in ast.walk(node):
        if not isinstance(child, ast.Call):
            continue

        if _called_name(child) == called_name:
            lines.append(child.lineno)

    return lines


def module_scope_bootstrap_call_count() -> int:
    count = 0

    for statement in _environment_tree().body:
        if isinstance(statement, ast.FunctionDef):
            continue

        count += len(_call_lines(statement, _BOOTSTRAP_NAME))

    return count


def _function_body(function_name: str) -> list[ast.stmt]:
    for node in _environment_tree().body:
        if not isinstance(node, ast.FunctionDef):
            continue

        if node.name == function_name:
            return node.body

    return []


def call_lines_in_function(
    function_name: str, called_name: str
) -> list[int]:
    lines: list[int] = []

    for statement in _function_body(function_name):
        lines.extend(_call_lines(statement, called_name))

    return sorted(lines)


def module_scope_url_fallback_is_present() -> bool:
    for node in _environment_tree().body:
        if not isinstance(node, ast.If):
            continue

        if not _call_lines(node.test, _GET_MAIN_OPTION):
            continue

        for statement in node.body:
            if _call_lines(statement, _SET_MAIN_OPTION):
                return True

    return False
