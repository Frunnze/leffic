"""Resolve explicit imports and re-exports against the files actually analyzed."""

from pathlib import Path


def source_root(path: Path, scan_roots=(), explicit_roots=()) -> Path:
    path = path.resolve()
    matches = [root for root in explicit_roots if path.is_relative_to(root)]
    if matches:
        return max(matches, key=lambda root: len(root.parts))
    markers = (
        ("pyproject.toml", "setup.cfg", "setup.py")
        if path.suffix == ".py"
        else ("package.json", "tsconfig.json")
    )
    for parent in path.parents:
        if parent.name == "src" or any((parent / name).is_file() for name in markers):
            return parent
    package = path.parent
    while (package / "__init__.py").is_file():
        package = package.parent
    if package != path.parent:
        return package
    matches = [root for root in scan_roots if path.is_relative_to(root)]
    return max(matches, key=lambda root: len(root.parts)) if matches else path.parent


class ImportResolver:
    def __init__(self, parsed: list[dict]) -> None:
        self.files = {item["path"]: item for item in parsed}
        self.absolute = {Path(path).resolve(): path for path in self.files}
        self.symbols = {
            path: {fact.name for fact in item["facts"]}
            for path, item in self.files.items()
        }
        self.roots = {
            path: Path(item["root"]).resolve()
            if item.get("root")
            else source_root(Path(path))
            for path, item in self.files.items()
        }
        self.cache: dict[tuple[str, str], list[tuple[str, str]]] = {}

    def resolve(self, path: str, reference: str) -> list[tuple[str, str]]:
        key = (path, reference)
        if key not in self.cache:
            targets = self.references(path, reference, frozenset())
            self.cache[key] = sorted(targets) if len(targets) == 1 else []
        return self.cache[key]

    def references(self, path: str, reference: str, seen: frozenset) -> set:
        key = (path, reference)
        if key in seen or len(seen) >= 64 or reference.startswith("local:"):
            return set()
        seen = seen | {key}
        candidates = set()
        for target, symbol in self.module_targets(path, reference):
            candidates.update(self.exported(target, symbol, seen))
        return candidates

    def module_targets(self, path: str, reference: str) -> set:
        candidates = set()
        if reference.startswith("local:"):
            return candidates
        file = Path(path).resolve()
        if file.suffix != ".py":
            for module, resolved in self.files[path].get("modules", {}).items():
                target = self.absolute.get(Path(resolved).resolve())
                if target and reference.startswith(module + "."):
                    candidates.add((target, reference[len(module) + 1 :]))
            return candidates
        root = self.roots[path]
        if reference.startswith("."):
            level = len(reference) - len(reference.lstrip("."))
            package = file.parent.relative_to(root).parts
            if level > len(package):
                return set()
            reference = ".".join(
                (*package[: len(package) - level + 1], reference.lstrip("."))
            )
        for index, character in enumerate(reference):
            if character != ".":
                continue
            imported = root.joinpath(*reference[:index].split("."))
            for alternative in (Path(str(imported) + ".py"), imported / "__init__.py"):
                target = self.absolute.get(alternative.resolve())
                if target and self.roots[target] == root:
                    candidates.add((target, reference[index + 1 :]))
        return candidates

    def exported(self, path: str, symbol: str, seen: frozenset) -> set:
        key = (path, "export:" + symbol)
        if key in seen or len(seen) >= 64:
            return set()
        seen = seen | {key}
        head, separator, tail = symbol.partition(".")
        suffix = separator + tail
        full = "<module>." + symbol
        item = self.files[path]
        export = item.get("exports", {}).get(head)
        if export is None and item.get("export_equals"):
            export = item["export_equals"]
            suffix = "." + symbol
        if isinstance(export, str):
            local = export + suffix
            return {(path, local)} if local in self.symbols[path] else set()
        if export:
            return self.references(path, export["reference"] + suffix, seen)
        if Path(path).suffix == ".py" and full in self.symbols[path]:
            return {(path, full)}
        candidates = set()
        if head != "default":
            for module in item.get("export_stars", []):
                candidates.update(self.references(path, module + "." + symbol, seen))
        return candidates
