import json
import subprocess
import tempfile
from pathlib import Path

from check_support import repository, run_check, stage_file
from hypothesis import HealthCheck, settings
from hypothesis import strategies as st

REPOSITORY = Path(__file__).resolve().parent.parent.parent
CHECK_NAME = "tracked-lockfiles"
CHECK_SCRIPT = REPOSITORY / "hooks" / "checks" / CHECK_NAME / "check"
TO_DOS = REPOSITORY / "docs" / "to-dos.md"
NPM_PACKAGES = ("ui-service", "api-gateway")
TRACKED_LOCKFILES = (
    "ui-service/package-lock.json",
    "api-gateway/package-lock.json",
    "hooks/package-lock.json",
)
EXPECTED_OVERRIDES = {
    "ui-service": {"tar": "^7.5.1", "qs": "^6.15.2"},
    "api-gateway": {"qs": "^6.15.2"},
}
DOCKERIGNORE_PATTERNS = ("node_modules", "dist", "tests", ".DS_Store")
HOOK_OUTPUT_PREFIX = "pre-commit:"
DECOY_LOCKFILE_PATHS = (
    "ui-service/package-lock.json/inner.json",
    "ui-service/nested/package-lock.json",
    "ui-service/package-lock.json.bak",
)
GATEWAY_TO_DO_TERMS = ("api-gateway/Dockerfile", "npm install", "npm ci")
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
HYPOTHESIS_SETTINGS = settings(
    max_examples=8,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
CheckRun = subprocess.CompletedProcess[str]


def git(*arguments: str) -> CheckRun:
    return subprocess.run(
        ["git", *arguments],
        cwd=REPOSITORY,
        capture_output=True,
        text=True,
        check=False,
    )


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


def stderr_lines(finished: CheckRun) -> list[str]:
    return [line for line in finished.stderr.splitlines() if line.strip()]


def recorded_overrides(package: str) -> dict[str, str]:
    lockfile = REPOSITORY / package / "package-lock.json"
    recorded = json.loads(lockfile.read_text(encoding="utf-8"))

    return recorded["packages"][""]["overrides"]


def declared_overrides(package: str) -> dict[str, str]:
    manifest = REPOSITORY / package / "package.json"

    return json.loads(manifest.read_text(encoding="utf-8"))["overrides"]


def gateway_to_do_items() -> list[str]:
    to_dos = TO_DOS.read_text(encoding="utf-8")

    return [
        item
        for item in to_dos.split("- [ ]")[1:]
        if all(term in item for term in GATEWAY_TO_DO_TERMS)
    ]


def completed_lockfile_items() -> list[str]:
    to_dos = TO_DOS.read_text(encoding="utf-8")

    return [
        item
        for item in to_dos.split("- [x]")[1:]
        if all(term in item for term in COMPLETED_TO_DO_TERMS)
    ]


def pre_commit_check_order() -> list[str]:
    hook = (REPOSITORY / "hooks" / "pre-commit").read_text(encoding="utf-8")

    return hook.split('checks_cheapest_first="')[1].split()


def dockerignore_patterns() -> tuple[str, ...]:
    ignored = REPOSITORY / "ui-service" / ".dockerignore"

    return tuple(ignored.read_text(encoding="utf-8").split())


def docker_build_of_clean_export(tmp_path: Path) -> int:
    archive = tmp_path / "ui-service.tar"
    export_directory = tmp_path / "export"
    export_directory.mkdir()
    exported = git("archive", "-o", str(archive), "HEAD", "ui-service")

    if exported.returncode:
        raise RuntimeError(exported.stderr)

    _ = subprocess.run(
        ["tar", "-x", "-f", str(archive), "-C", str(export_directory)],
        check=True,
    )
    built = subprocess.run(
        ["docker", "build", str(export_directory / "ui-service")],
        capture_output=True,
        check=False,
    )

    return built.returncode
