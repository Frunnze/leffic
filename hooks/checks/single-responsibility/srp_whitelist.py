"""Exact, explained exceptions for reviewed SRP findings; keep raw evidence."""

import json
from pathlib import Path

DEFAULT_WHITELIST = Path(__file__).with_name("whitelist.txt")


def read_whitelist(path: Path) -> dict[tuple[Path, str, str], str]:
    entries = {}
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), 1
    ):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        try:
            entry = json.loads(line)
            if (
                not isinstance(entry, dict)
                or set(entry) != {"path", "kind", "name", "reason"}
                or not all(
                    isinstance(value, str) and value.strip() for value in entry.values()
                )
                or entry["kind"] not in {"callable", "class", "module"}
            ):
                raise ValueError(
                    "expected nonempty path, kind, name and reason strings"
                )
            key = (Path(entry["path"]).resolve(), entry["kind"], entry["name"])
            if key in entries:
                raise ValueError("duplicate finding")
            entries[key] = entry["reason"].strip()
        except ValueError as error:
            raise ValueError(
                f"invalid SRP whitelist {path}:{line_number}: {error}"
            ) from error
    return entries


def apply_whitelist(reports: list[dict], entries: dict) -> dict:
    count = 0
    for report in reports:
        path = Path(report["path"]).resolve()
        report["raw_coefficient"] = report["coefficient"]
        for unit in report["units"]:
            reason = entries.get((path, unit["kind"], unit["name"]))
            unit["whitelisted"] = reason is not None
            if reason is not None:
                unit["whitelist_reason"] = reason
                count += 1
        report["coefficient"] = max(
            (
                unit["coefficient"]
                for unit in report["units"]
                if not unit["whitelisted"]
            ),
            default=0.0,
        )
    return {
        "coefficient": max((report["coefficient"] for report in reports), default=0.0),
        "raw_coefficient": max(
            (report["raw_coefficient"] for report in reports), default=0.0
        ),
        "whitelisted_count": count,
    }
