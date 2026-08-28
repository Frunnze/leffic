import json
import tempfile
from pathlib import Path

from check_support import (
    NPM_PACKAGES,
    REPOSITORY,
    CheckRun,
    repository,
    run_check,
    stage_file,
)
from hypothesis import strategies as st

CHECK_NAME = "tracked-lockfiles"
CHECK_SCRIPT = REPOSITORY / "hooks" / "checks" / CHECK_NAME / "check"
TO_DOS = REPOSITORY / "docs" / "to-dos.md"
TRACKED_LOCKFILES = (
    "ui-service/package-lock.json",
    "api-gateway/package-lock.json",
    "hooks/package-lock.json",
)
EXPECTED_OVERRIDES = {
    "ui-service": {"tar": "^7.5.1", "qs": "^6.15.2"},
    "api-gateway": {"qs": "^6.15.2"},
}
DECOY_LOCKFILE_PATHS = (
    "ui-service/package-lock.json/inner.json",
    "ui-service/nested/package-lock.json",
    "ui-service/package-lock.json.bak",
)
COMPLETED_TO_DO_TERMS = (
    "ui-service/package-lock.json",
    "pnpm-lock.yaml",
    ".gitignore",
    "tracked-lockfiles",
    "git archive HEAD ui-service",
    "docker build",
)
CLAIM_MARKER = "claimed 2026-08-28T15:30Z"
EXIT_EXPECTATIONS = (
    ((), 1),
    (("ui-service",), 1),
    (("api-gateway",), 1),
    (NPM_PACKAGES, 0),
)
PACKAGE_SUBSETS = st.lists(
    st.sampled_from(NPM_PACKAGES), unique=True
).map(tuple)


def fixture_repository(tmp_path: Path, tracked: tuple[str, ...]) -> Path:
    root = Path(tempfile.mkdtemp(dir=tmp_path))
    repository(root)

    for package in NPM_PACKAGES:
        stage_file(root, f"{package}/src/main.ts", "export const a = 1;\n")

    for package in tracked:
        stage_file(root, f"{package}/package-lock.json", "{}\n")

    return root


def run_for(tmp_path: Path, tracked: tuple[str, ...]) -> CheckRun:
    return run_check(fixture_repository(tmp_path, tracked), CHECK_NAME)


def run_with_unstaged_lockfile(tmp_path: Path) -> CheckRun:
    root = fixture_repository(tmp_path, ("api-gateway",))
    lockfile = root / "ui-service" / "package-lock.json"
    _ = lockfile.write_text("{}\n", encoding="utf-8")

    return run_check(root, CHECK_NAME)


def run_with_decoy_lockfile(tmp_path: Path, decoy: str) -> CheckRun:
    root = fixture_repository(tmp_path, ("api-gateway",))
    stage_file(root, decoy, "{}\n")

    return run_check(root, CHECK_NAME)


def run_with_extra_package(tmp_path: Path) -> CheckRun:
    root = fixture_repository(tmp_path, NPM_PACKAGES)
    stage_file(root, "extra-service/src/main.ts", "export const a = 1;\n")

    return run_check(root, CHECK_NAME)


def run_with_deleted_lockfile(tmp_path: Path) -> CheckRun:
    root = fixture_repository(tmp_path, NPM_PACKAGES)
    (root / "ui-service" / "package-lock.json").unlink()

    return run_check(root, CHECK_NAME)


def recorded_overrides(package: str) -> dict[str, str]:
    lockfile = REPOSITORY / package / "package-lock.json"
    recorded = json.loads(lockfile.read_text(encoding="utf-8"))

    return recorded["packages"][""]["overrides"]


def declared_overrides(package: str) -> dict[str, str]:
    manifest = REPOSITORY / package / "package.json"

    return json.loads(manifest.read_text(encoding="utf-8"))["overrides"]


def completed_lockfile_items() -> list[str]:
    to_dos = TO_DOS.read_text(encoding="utf-8")

    return [
        item
        for item in to_dos.split("- [x]")[1:]
        if all(term in item for term in COMPLETED_TO_DO_TERMS)
    ]
