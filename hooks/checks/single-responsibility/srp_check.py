"""Run both AST adapters and report the maximum SRP coefficient (no averaging)."""

import argparse
import json
import sys
from os.path import commonpath
from pathlib import Path

from python_facts import python_facts
from srp_call_aliases import resolve_call_aliases
from srp_clients import caller_index
from srp_cohesion import owner_score
from srp_delegation import effect_call_graph, summarize_effects
from srp_imports import source_root
from srp_inputs import SUFFIXES, source_paths, typescript_facts
from srp_metrics import THRESHOLD, CallableFacts, callable_score
from srp_whitelist import DEFAULT_WHITELIST, apply_whitelist, read_whitelist


def report_for(
    path: str,
    facts: list[CallableFacts],
    owners: list[dict],
    clients: dict | None = None,
) -> dict:
    units = [callable_score(item) for item in facts if not item.client_only]
    units.extend(
        owner_score({**owner, "path": path}, facts, clients) for owner in owners
    )
    units.sort(key=lambda unit: (unit["line"], unit["name"], unit["kind"]))
    return {
        "path": path,
        "coefficient": max(
            (unit["coefficient"] for unit in units),
            default=0.0,
        ),
        "units": units,
    }


def analyze(
    paths: list[Path],
    node: str,
    module: str | None,
    source_roots=(),
    scan_roots=(),
    tsconfig=None,
    whitelist=None,
) -> dict:
    whitelist_path = Path(whitelist) if whitelist is not None else DEFAULT_WHITELIST
    exceptions = read_whitelist(whitelist_path)
    source_roots = [Path(root).resolve() for root in source_roots]
    if any(not root.is_dir() for root in source_roots):
        raise ValueError("every --source-root must be an existing directory")
    scan_roots = [Path(root).resolve() for root in scan_roots]
    if not scan_roots and paths:
        scan_roots = [Path(commonpath([path.resolve().parent for path in paths]))]
    parsed_files = []
    for path in paths:
        if path.suffix == ".py":
            exports = {}
            facts, owners = python_facts(path, exports)
            parsed_files.append(
                {
                    "path": str(path),
                    "facts": facts,
                    "owners": owners,
                    "exports": exports,
                }
            )
    for parsed in typescript_facts(
        [path for path in paths if path.suffix in SUFFIXES - {".py"}],
        node,
        module,
        tsconfig,
    ):
        facts = [CallableFacts(**item) for item in parsed["callables"]]
        parsed_files.append({**parsed, "facts": facts})
    for item in parsed_files:
        item["root"] = str(source_root(Path(item["path"]), scan_roots, source_roots))
    clients = caller_index(parsed_files)
    effects = effect_call_graph(parsed_files)
    resolve_call_aliases(parsed_files)
    summarize_effects(parsed_files, effects)
    reports = [
        {
            **report_for(item["path"], item["facts"], item["owners"], clients),
            "source_root": item["root"],
        }
        for item in parsed_files
    ]
    reports.sort(key=lambda report: report["path"])
    summary = apply_whitelist(reports, exceptions)
    return {
        "schema_version": 5,
        **summary,
        "whitelist_path": str(whitelist_path.resolve()),
        "threshold": THRESHOLD,
        "failed": summary["coefficient"] >= THRESHOLD,
        "files": reports,
        "typescript_configs": sorted(
            {item["config"] for item in parsed_files if item.get("config")}
        ),
    }


def print_report(report: dict) -> None:
    print(
        f"pre-commit: SRP coefficient={report['coefficient']:.12f} "
        f"threshold={THRESHOLD} files={len(report['files'])} "
        f"whitelisted={report['whitelisted_count']}"
    )
    for file in report["files"]:
        for unit in file["units"]:
            if unit["coefficient"] < THRESHOLD or unit["whitelisted"]:
                continue
            print(
                f"{file['path']}:{unit['line']}: {unit['name']} "
                f"SRP={unit['coefficient']:.12f}: " + "; ".join(unit["reasons"]),
                file=sys.stderr,
            )
    if report["failed"]:
        print(
            "pre-commit: follow SRP - Agent: first identify whether each "
            "finding is a real SRP violation. Fix only the real violations. "
            "If a finding is not one, never refactor it - whitelist it: add "
            f"the exact finding and a reason to {report['whitelist_path']}",
            file=sys.stderr,
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", help="source files or directories")
    parser.add_argument("--json", action="store_true", help="include every score")
    parser.add_argument("--node", default="node")
    parser.add_argument(
        "--whitelist",
        help="reviewed exceptions file; defaults to whitelist.txt beside this check",
    )
    parser.add_argument(
        "--source-root",
        action="append",
        default=[],
        help="explicit import root for a namespace or nonstandard source layout; repeatable",
    )
    parser.add_argument(
        "--typescript",
        help="installed TypeScript package directory; otherwise discovered locally",
    )
    parser.add_argument(
        "--tsconfig",
        help="explicit TypeScript config; otherwise discover the nearest tsconfig.json",
    )
    args = parser.parse_args()
    try:
        report = analyze(
            source_paths(args.paths),
            args.node,
            args.typescript,
            args.source_root,
            [Path(path) for path in args.paths if Path(path).is_dir()],
            args.tsconfig,
            args.whitelist,
        )
    except SyntaxError as error:
        print(
            f"pre-commit: SRP analysis error: {error.filename}:"
            f"{error.lineno}: {error.msg}",
            file=sys.stderr,
        )
        return 2
    except (OSError, ValueError) as error:
        print(f"pre-commit: SRP analysis error: {error}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(report, sort_keys=True))
    else:
        print_report(report)
    return int(report["failed"])


if __name__ == "__main__":
    sys.exit(main())
