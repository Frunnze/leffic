"""Resolve explicit imports and simple aliases without guessing from names."""

import ast

SCOPES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)
FUNCTIONS = (ast.FunctionDef, ast.AsyncFunctionDef)


def qualified(node: ast.AST | None, bindings: dict[str, str] | None = None) -> str:
    if isinstance(node, ast.Name):
        return (
            bindings.get(node.id, "local:" + node.id)
            if bindings is not None
            else node.id
        )
    if isinstance(node, ast.Attribute):
        if bindings is not None and qualified(node) in bindings:
            return bindings[qualified(node)]
        base = qualified(node.value, bindings)
        return f"{base}.{node.attr}" if base else ""
    if isinstance(node, ast.Call):
        return qualified(node.func, bindings)
    if isinstance(node, ast.Subscript):
        return qualified(node.value, bindings)
    return ""


def scope_nodes(node: ast.AST):
    for child in ast.iter_child_nodes(node):
        yield child
        if not isinstance(child, SCOPES):
            yield from scope_nodes(child)


def imports_in(node: ast.AST) -> dict[str, str]:
    bindings: dict[str, str] = {}
    for child in scope_nodes(node):
        if isinstance(child, ast.Import):
            for alias in child.names:
                bindings[alias.asname or alias.name.split(".")[0]] = (
                    alias.name if alias.asname else alias.name.split(".")[0]
                )
        elif isinstance(child, ast.ImportFrom):
            prefix = "." * child.level + (child.module or "")
            for alias in child.names:
                separator = "." if child.module else ""
                bindings[alias.asname or alias.name] = (
                    f"{prefix}{separator}{alias.name}"
                )
    return bindings


def bound_names(node: ast.AST) -> set[str]:
    return {
        child.id
        for child in ast.walk(node)
        if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Store)
    }


def capture_name(node: ast.AST) -> str:
    if isinstance(node, (ast.ExceptHandler, ast.MatchAs, ast.MatchStar)):
        return node.name or ""
    if isinstance(node, ast.MatchMapping):
        return node.rest or ""
    return ""


def annotation_type(node: ast.AST | None, bindings: dict[str, str], depth=0) -> str:
    if node is None or depth > 12:
        return ""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        try:
            node = ast.parse(node.value, mode="eval").body
        except SyntaxError:
            return ""
        return annotation_type(node, bindings, depth + 1)
    if isinstance(node, ast.Subscript):
        wrapper = qualified(node.value, bindings)
        values = node.slice.elts if isinstance(node.slice, ast.Tuple) else [node.slice]
        if wrapper in {
            "typing.Annotated",
            "typing_extensions.Annotated",
            "typing.Optional",
        }:
            return annotation_type(values[0], bindings, depth + 1)
        if wrapper == "typing.Union":
            return union_type(values, bindings, depth + 1)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
        return union_type([node.left, node.right], bindings, depth + 1)
    resolved = qualified(node, bindings)
    return resolved if resolved and not resolved.startswith("local:") else ""


def union_type(nodes: list[ast.AST], bindings: dict[str, str], depth: int) -> str:
    types = {
        annotation_type(node, bindings, depth)
        for node in nodes
        if not (isinstance(node, ast.Constant) and node.value is None)
    }
    return next(iter(types)) if len(types) == 1 and "" not in types else ""


def local_bindings(node: ast.AST, inherited: dict[str, str]) -> dict[str, str]:
    bindings = dict(inherited)
    for child in scope_nodes(node):
        if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Store):
            bindings[child.id] = "local:" + child.id
        elif isinstance(child, (ast.ClassDef, *FUNCTIONS)):
            bindings[child.name] = "local:" + child.name
        elif name := capture_name(child):
            bindings[name] = "local:" + name
    if isinstance(node, (*FUNCTIONS, ast.Lambda)):
        arguments = (
            *node.args.posonlyargs,
            *node.args.args,
            *node.args.kwonlyargs,
            node.args.vararg,
            node.args.kwarg,
        )
        for argument in arguments:
            if argument is not None:
                bindings[argument.arg] = "local:" + argument.arg
                annotation = annotation_type(argument.annotation, inherited)
                if annotation:
                    bindings[argument.arg] = annotation
    bindings.update(imports_in(node))
    return bindings


def assigned_value(value: ast.AST | None, bindings: dict[str, str]) -> str:
    if isinstance(value, ast.Subscript) and qualified(value.value, bindings) in {
        "typing.Annotated",
        "typing_extensions.Annotated",
        "typing.Optional",
        "typing.Union",
    }:
        return annotation_type(value, bindings)
    resolved = qualified(value, bindings)
    if isinstance(value, ast.Call):
        tail = resolved.rsplit(".", 1)[-1]
        if not (tail[:1].isupper() or tail in {"open", "connect", "cursor"}):
            return ""
    return resolved


def bind_assignment(node: ast.AST, bindings: dict[str, str]) -> None:
    if isinstance(node, ast.Assign):
        targets, value = node.targets, node.value
    elif isinstance(node, ast.AnnAssign):
        targets, value = [node.target], node.value
    elif isinstance(node, ast.TypeAlias):
        targets, value = [node.name], node.value
    elif isinstance(node, ast.withitem):
        targets, value = [node.optional_vars], node.context_expr
    else:
        return
    resolved = assigned_value(value, bindings)
    if isinstance(node, ast.AnnAssign):
        resolved = annotation_type(node.annotation, bindings) or resolved
    for target in targets:
        if isinstance(target, (ast.Name, ast.Attribute)):
            name = qualified(target)
            bindings[name] = resolved or "local:" + name


def is_docstring(node: ast.AST) -> bool:
    return (
        isinstance(node, ast.Expr)
        and isinstance(node.value, ast.Constant)
        and isinstance(node.value.value, str)
    )
