import shutil
import subprocess
import sys
from pathlib import Path

from hypothesis import HealthCheck, settings

HOOKS = Path(__file__).resolve().parent.parent
REPOSITORY = HOOKS.parent
IGNORED = "hooks/\n.venv/\n"
NPM_PACKAGES = ("ui-service", "api-gateway")
HOOK_OUTPUT_PREFIX = "pre-commit:"
DOCKERIGNORE_PATTERNS = ("node_modules", "dist", "tests", ".DS_Store")
HYPOTHESIS_SETTINGS = settings(
    max_examples=8,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
CheckRun = subprocess.CompletedProcess[str]


def repository(tmp_path: Path) -> None:
    hooks = tmp_path / "hooks"
    hooks.mkdir()
    _ = shutil.copy2(HOOKS / "_env.sh", hooks / "_env.sh")
    _ = shutil.copytree(HOOKS / "checks", hooks / "checks")
    _ = (tmp_path / ".gitignore").write_text(IGNORED, encoding="utf-8")

    for command in (
        ["git", "init", "--quiet"],
        ["git", "config", "user.email", "hooks@example.com"],
        ["git", "config", "user.name", "hooks"],
    ):
        _ = subprocess.run(command, cwd=tmp_path, check=True)


def link_real_python(tmp_path: Path) -> None:
    binary = tmp_path / ".venv" / "bin" / "python"
    binary.parent.mkdir(parents=True, exist_ok=True)
    binary.symlink_to(Path(sys.executable))


def stub_binary(tmp_path: Path, name: str, body: str) -> None:
    binary = tmp_path / ".venv" / "bin" / name
    binary.parent.mkdir(parents=True, exist_ok=True)
    _ = binary.write_text(f"#!/bin/sh\n{body}", encoding="utf-8")
    binary.chmod(0o755)


def here_document(label: str, text: str) -> str:
    return f"cat <<'{label}'\n{text}{label}\n"


def stage_file(tmp_path: Path, relative: str, content: str) -> None:
    path = tmp_path / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    _ = path.write_text(content, encoding="utf-8")
    _ = subprocess.run(
        ["git", "add", relative], cwd=tmp_path, check=True
    )


def run_check(tmp_path: Path, name: str) -> CheckRun:
    return subprocess.run(
        ["sh", f"hooks/checks/{name}/check"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )


def stderr_lines(finished: CheckRun) -> list[str]:
    return [line for line in finished.stderr.splitlines() if line.strip()]


def git(*arguments: str) -> CheckRun:
    return subprocess.run(
        ["git", *arguments],
        cwd=REPOSITORY,
        capture_output=True,
        text=True,
        check=False,
    )


def registered_check_directories() -> list[str]:
    checks = HOOKS / "checks"

    return sorted(path.name for path in checks.iterdir() if path.is_dir())


def pre_commit_check_order() -> list[str]:
    hook = (HOOKS / "pre-commit").read_text(encoding="utf-8")

    declared = hook.split('checks_cheapest_first="')[1]

    return declared.split('"')[0].split()


def dockerignore_patterns(package: str) -> tuple[str, ...]:
    ignored = REPOSITORY / package / ".dockerignore"

    return tuple(ignored.read_text(encoding="utf-8").split())


def docker_build_of_clean_export(tmp_path: Path, package: str) -> int:
    archive = tmp_path / f"{package}.tar"
    export_directory = tmp_path / "export"
    export_directory.mkdir()
    exported = git("archive", "-o", str(archive), "HEAD", package)

    if exported.returncode:
        raise RuntimeError(exported.stderr)

    _ = subprocess.run(
        ["tar", "-x", "-f", str(archive), "-C", str(export_directory)],
        check=True,
    )
    built = subprocess.run(
        ["docker", "build", str(export_directory / package)],
        capture_output=True,
        check=False,
    )

    return built.returncode
