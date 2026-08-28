from pathlib import Path

from check_support import (
    HOOK_OUTPUT_PREFIX,
    NPM_PACKAGES,
    pre_commit_check_order,
    registered_check_directories,
    stderr_lines,
)
from gateway_dockerfile_facts import real_dockerfile
from reproducible_images_support import (
    CHECK_NAME,
    CHECK_SCRIPT,
    CONFORMING_DOCKERFILE,
    CONFORMING_PLAN,
    GATEWAY_PACKAGE,
    MISSING_LOCKFILE_DOCKERFILE,
    MISSING_NPM_CI_DOCKERFILE,
    NO_INSTALL_DOCKERFILE,
    NPM_INSTALL_DOCKERFILE,
    UI_PACKAGE,
    run_for,
    run_with_unreadable_dockerfile,
)


def test_r10_the_check_is_an_executable_posix_script() -> None:
    assert CHECK_SCRIPT.stat().st_mode & 0o111


def test_r10_the_check_starts_with_the_posix_shebang() -> None:
    source = CHECK_SCRIPT.read_text(encoding="utf-8")

    assert source.startswith("#!/bin/sh\n")
    assert "set -e" in source


def test_r10_the_check_sources_the_shared_environment() -> None:
    source = CHECK_SCRIPT.read_text(encoding="utf-8")

    assert '. "$(dirname "$0")/../../_env.sh"' in source


def test_r18_the_check_runs_third_in_the_pre_commit_order() -> None:
    assert pre_commit_check_order()[:3] == [
        "tracked-lockfiles",
        "secrets",
        CHECK_NAME,
    ]


def test_r19_every_check_directory_is_registered() -> None:
    registered = pre_commit_check_order()

    for directory in registered_check_directories():
        assert directory in registered


def test_r11_a_missing_lockfile_copy_fails(tmp_path: Path) -> None:
    plan = {GATEWAY_PACKAGE: MISSING_LOCKFILE_DOCKERFILE}
    finished = run_for(tmp_path, plan)

    assert finished.returncode == 1
    assert GATEWAY_PACKAGE in finished.stderr


def test_r12_an_npm_install_fails(tmp_path: Path) -> None:
    finished = run_for(tmp_path, {GATEWAY_PACKAGE: NPM_INSTALL_DOCKERFILE})

    assert finished.returncode == 1
    assert GATEWAY_PACKAGE in finished.stderr


def test_r13_a_dockerfile_without_npm_ci_fails(tmp_path: Path) -> None:
    finished = run_for(tmp_path, {UI_PACKAGE: MISSING_NPM_CI_DOCKERFILE})

    assert finished.returncode == 1
    assert UI_PACKAGE in finished.stderr


def test_r11_r13_a_dockerfile_that_installs_nothing_is_ignored(
    tmp_path: Path,
) -> None:
    plan = {package: NO_INSTALL_DOCKERFILE for package in NPM_PACKAGES}
    finished = run_for(tmp_path, plan)

    assert finished.returncode == 0
    assert stderr_lines(finished) == []


def test_r14_conforming_dockerfiles_pass(tmp_path: Path) -> None:
    assert run_for(tmp_path, CONFORMING_PLAN).returncode == 0


def test_r15_a_package_without_a_dockerfile_is_ignored(
    tmp_path: Path,
) -> None:
    plan = {UI_PACKAGE: CONFORMING_DOCKERFILE}

    assert run_for(tmp_path, plan).returncode == 0


def test_r16_every_failing_stderr_line_is_prefixed(tmp_path: Path) -> None:
    finished = run_for(tmp_path, {GATEWAY_PACKAGE: NPM_INSTALL_DOCKERFILE})

    assert stderr_lines(finished)
    for line in stderr_lines(finished):
        assert line.startswith(HOOK_OUTPUT_PREFIX)


def test_r16_an_unreadable_dockerfile_fails_with_a_prefixed_line(
    tmp_path: Path,
) -> None:
    finished = run_with_unreadable_dockerfile(tmp_path)

    assert finished.returncode == 1
    assert GATEWAY_PACKAGE in finished.stderr
    for line in stderr_lines(finished):
        assert line.startswith(HOOK_OUTPUT_PREFIX)


def test_r17_a_passing_run_prints_its_rationale(tmp_path: Path) -> None:
    finished = run_for(tmp_path, CONFORMING_PLAN)

    assert finished.stdout.startswith(HOOK_OUTPUT_PREFIX)
    assert len(finished.stdout.splitlines()) == 1


def test_r14_the_real_dockerfiles_pass_the_check(tmp_path: Path) -> None:
    plan = {package: real_dockerfile(package) for package in NPM_PACKAGES}

    assert run_for(tmp_path, plan).returncode == 0


def test_r11_r12_a_regressed_gateway_dockerfile_fails(
    tmp_path: Path,
) -> None:
    regressed = real_dockerfile(GATEWAY_PACKAGE).replace(
        "npm ci", "npm install"
    )
    plan = dict(CONFORMING_PLAN, **{GATEWAY_PACKAGE: regressed})
    finished = run_for(tmp_path, plan)

    assert finished.returncode == 1
    assert GATEWAY_PACKAGE in finished.stderr
