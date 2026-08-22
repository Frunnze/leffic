from pathlib import Path

from check_support import (
    here_document,
    repository,
    run_check,
    stage_file,
    stub_binary,
)

SERVICE = "user-service"
STAGED_SOURCE = f"{SERVICE}/src/thing.py"
KILLED = "    thing.xǁThingǁgo__mutmut_1: killed\n"
SURVIVED = "    thing.xǁThingǁgo__mutmut_1: survived\n"
ELSEWHERE = "    other.xǁOtherǁgo__mutmut_1: killed\n"
IMPORT_FAILURE = "mutmut: could not import src\n"


def _mutmut_reporting(results: str, run_output: str) -> str:
    return (
        'if [ "$1" = "results" ]; then\n'
        f"{here_document('RESULTS_EOF', results)}"
        "exit 0\n"
        "fi\n"
        f"{here_document('RUN_EOF', run_output)}"
        "exit 0\n"
    )


def _repository_with(
    tmp_path: Path, results: str, run_output: str = ""
) -> None:
    repository(tmp_path)
    stub_binary(
        tmp_path, "mutmut", _mutmut_reporting(results, run_output)
    )
    stage_file(
        tmp_path, STAGED_SOURCE, "def go(value):\n    return value\n"
    )


def test_fails_when_the_service_builds_no_mutants(tmp_path: Path) -> None:
    _repository_with(tmp_path, results="", run_output=IMPORT_FAILURE)
    finished = run_check(tmp_path, "mutation")

    assert finished.returncode == 1
    assert "could not import src" in finished.stderr


def test_says_so_when_nothing_staged_has_a_mutant(tmp_path: Path) -> None:
    _repository_with(tmp_path, results=ELSEWHERE)
    finished = run_check(tmp_path, "mutation")

    assert finished.returncode == 0
    assert "no mutant" in finished.stdout


def test_passes_when_every_staged_mutant_is_killed(tmp_path: Path) -> None:
    _repository_with(tmp_path, results=KILLED)

    assert run_check(tmp_path, "mutation").returncode == 0


def test_fails_when_a_staged_mutant_survives(tmp_path: Path) -> None:
    _repository_with(tmp_path, results=SURVIVED)
    finished = run_check(tmp_path, "mutation")

    assert finished.returncode == 1
    assert "survived" in finished.stderr
