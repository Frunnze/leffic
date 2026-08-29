from pathlib import Path

_WHITELIST_PATH = (
    Path(__file__).resolve().parents[1]
    / "checks"
    / "dead-code"
    / "vulture_whitelist.py"
)
_ENTRY_POINT_NAME = "create_postgres_database_if_configured"


def _whitelist_lines() -> list[str]:
    source = _WHITELIST_PATH.read_text(encoding="utf-8")

    return [line for line in source.splitlines() if line.strip()]


def _lines_naming_the_migration_bootstrap() -> list[str]:
    named: list[str] = []

    for line in _whitelist_lines():
        if line.split("#")[0].strip() == _ENTRY_POINT_NAME:
            named.append(line)

    return named


def test_the_migration_bootstrap_is_whitelisted_once() -> None:
    assert len(_lines_naming_the_migration_bootstrap()) == 1
