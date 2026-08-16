import shutil
import subprocess
import sys
from pathlib import Path

HOOKS = Path(__file__).parent.parent
IGNORED = "hooks/\n.venv/\n"


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


def run_check(
    tmp_path: Path, name: str
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["sh", f"hooks/checks/{name}/check"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )
