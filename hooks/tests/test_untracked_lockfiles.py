from pathlib import Path

import pytest
from check_support import (
    DOCKERIGNORE_PATTERNS,
    HOOK_OUTPUT_PREFIX,
    HYPOTHESIS_SETTINGS,
    NPM_PACKAGES,
    REPOSITORY,
    docker_build_of_clean_export,
    dockerignore_patterns,
    git,
    pre_commit_check_order,
    repository,
    run_check,
    stage_file,
    stderr_lines,
)
from hypothesis import given
from hypothesis import strategies as st
from lockfile_check_support import (
    CHECK_NAME,
    CHECK_SCRIPT,
    CLAIM_MARKER,
    DECOY_LOCKFILE_PATHS,
    EXIT_EXPECTATIONS,
    EXPECTED_OVERRIDES,
    PACKAGE_SUBSETS,
    TO_DOS,
    TRACKED_LOCKFILES,
    completed_lockfile_items,
    declared_overrides,
    recorded_overrides,
    run_for,
    run_with_decoy_lockfile,
    run_with_deleted_lockfile,
    run_with_extra_package,
    run_with_unstaged_lockfile,
)


def test_r1_no_rule_ignores_a_package_lock() -> None:
    ignored = (REPOSITORY / ".gitignore").read_text(encoding="utf-8")

    assert "package-lock.json" not in ignored
    assert git("check-ignore", "ui-service/package-lock.json").returncode


@pytest.mark.parametrize("lockfile", TRACKED_LOCKFILES)
def test_r2_r3_r4_lockfile_is_tracked(lockfile: str) -> None:
    assert git("ls-files", lockfile).stdout.strip() == lockfile


def test_r5_the_pnpm_lock_is_gone() -> None:
    assert git("ls-files", "ui-service/pnpm-lock.yaml").stdout == ""
    assert not (REPOSITORY / "ui-service" / "pnpm-lock.yaml").exists()


@pytest.mark.parametrize("package", NPM_PACKAGES)
def test_r6_r7_lockfile_records_declared_overrides(package: str) -> None:
    assert recorded_overrides(package) == EXPECTED_OVERRIDES[package]


def test_r8_check_is_an_executable_posix_script() -> None:
    source = CHECK_SCRIPT.read_text(encoding="utf-8")

    assert CHECK_SCRIPT.stat().st_mode & 0o111
    assert source.startswith("#!/bin/sh\n")
    assert "set -e" in source
    assert '. "$(dirname "$0")/../../_env.sh"' in source


def test_r13_check_runs_first_in_the_pre_commit_order() -> None:
    assert pre_commit_check_order()[:2] == [CHECK_NAME, "secrets"]


@pytest.mark.parametrize("package", NPM_PACKAGES)
def test_r14_r21_dockerignore_lists_exactly_four_patterns(
    package: str,
) -> None:
    assert dockerignore_patterns(package) == DOCKERIGNORE_PATTERNS


def test_r16_the_finished_item_records_every_part_of_the_change() -> None:
    assert completed_lockfile_items()


def test_r17_the_claim_marker_is_removed() -> None:
    assert CLAIM_MARKER not in TO_DOS.read_text(encoding="utf-8")


def test_r20_the_change_lands_on_main() -> None:
    assert git("branch", "--show-current").stdout.strip() == "main"


@pytest.mark.parametrize("tracked, expected", EXIT_EXPECTATIONS)
def test_r9_r10_exit_code_follows_the_tracked_lockfiles(
    tmp_path: Path, tracked: tuple[str, ...], expected: int
) -> None:
    assert run_for(tmp_path, tracked).returncode == expected


def test_r10_an_unstaged_lockfile_does_not_count(tmp_path: Path) -> None:
    assert run_with_unstaged_lockfile(tmp_path).returncode == 1


def test_r11_every_failing_stderr_line_is_prefixed(tmp_path: Path) -> None:
    finished = run_for(tmp_path, ())

    assert stderr_lines(finished)
    for line in stderr_lines(finished):
        assert line.startswith(HOOK_OUTPUT_PREFIX)


def test_r12_a_passing_run_prints_its_rationale(tmp_path: Path) -> None:
    finished = run_for(tmp_path, NPM_PACKAGES)

    assert finished.stdout.startswith(HOOK_OUTPUT_PREFIX)


@pytest.mark.parametrize("package", NPM_PACKAGES)
def test_r7_r15_r20_a_clean_export_of_each_package_builds(
    tmp_path: Path, package: str
) -> None:
    assert docker_build_of_clean_export(tmp_path, package) == 0


@given(tracked=PACKAGE_SUBSETS)
@HYPOTHESIS_SETTINGS
def test_tracked_lockfiles_property_passes_only_when_all_tracked(
    tmp_path: Path, tracked: tuple[str, ...]
) -> None:
    passed = run_for(tmp_path, tracked).returncode == 0

    assert passed is (set(tracked) == set(NPM_PACKAGES))


@given(tracked=PACKAGE_SUBSETS)
@HYPOTHESIS_SETTINGS
def test_tracked_lockfiles_property_prefixes_every_stderr_line(
    tmp_path: Path, tracked: tuple[str, ...]
) -> None:
    finished = run_for(tmp_path, tracked)

    for line in stderr_lines(finished):
        assert line.startswith(HOOK_OUTPUT_PREFIX)


@given(tracked=PACKAGE_SUBSETS)
@HYPOTHESIS_SETTINGS
def test_tracked_lockfiles_property_names_each_untracked_package(
    tmp_path: Path, tracked: tuple[str, ...]
) -> None:
    finished = run_for(tmp_path, tracked)

    for package in set(NPM_PACKAGES) - set(tracked):
        assert package in finished.stderr


@given(package=st.sampled_from(NPM_PACKAGES))
def test_committed_lockfile_property_mirrors_declared_overrides(
    package: str,
) -> None:
    assert recorded_overrides(package) == declared_overrides(package)


@pytest.mark.parametrize("decoy", DECOY_LOCKFILE_PATHS)
def test_fuzz_a_lookalike_path_does_not_satisfy_the_check(
    tmp_path: Path, decoy: str
) -> None:
    finished = run_with_decoy_lockfile(tmp_path, decoy)

    assert finished.returncode == 1
    assert "ui-service" in finished.stderr


def test_fuzz_an_undeclared_package_is_not_policed(tmp_path: Path) -> None:
    assert run_with_extra_package(tmp_path).returncode == 0


def test_fuzz_a_package_without_sources_is_not_policed(
    tmp_path: Path,
) -> None:
    repository(tmp_path)
    stage_file(tmp_path, "ui-service/src/main.ts", "export const a = 1;\n")
    stage_file(tmp_path, "ui-service/package-lock.json", "{}\n")

    assert run_check(tmp_path, CHECK_NAME).returncode == 0


def test_fuzz_a_lockfile_deleted_from_the_worktree_still_passes(
    tmp_path: Path,
) -> None:
    assert run_with_deleted_lockfile(tmp_path).returncode == 0
