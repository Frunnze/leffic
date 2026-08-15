import subprocess
import sys
from pathlib import Path

CHECKER = (
    Path(__file__).parent.parent / "checks" / "property_test_coverage.py"
)
SOURCE = Path("service/src/features/study_units/scheduler.py")
TESTS = Path("service/tests/test_scheduler.py")


def report_for(tmp_path: Path, source: str, tests: str) -> list[str]:
    written = [
        _write(tmp_path, SOURCE, source),
        _write(tmp_path, TESTS, tests),
    ]
    finished = subprocess.run(
        [sys.executable, str(CHECKER)],
        input="\n".join(written),
        capture_output=True,
        text=True,
        check=True,
        cwd=tmp_path,
    )

    return finished.stdout.splitlines()


def missing(name: str, line_number: int) -> str:
    return (
        f"{SOURCE}:{line_number}: {name} needs a property test "
        f"named test_{name}_property*"
    )


def given_test(name: str, decorators: str = "@given()") -> str:
    return (
        "from hypothesis import given, settings\n"
        f"{decorators}\n"
        f"def {name}():\n"
        "    pass\n"
    )


def _write(tmp_path: Path, relative: Path, source: str) -> str:
    module = tmp_path / relative
    module.parent.mkdir(parents=True, exist_ok=True)
    _ = module.write_text(source, encoding="utf-8")

    return str(relative)
