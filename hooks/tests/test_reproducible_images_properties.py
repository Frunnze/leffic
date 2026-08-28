from pathlib import Path

from check_support import (
    HOOK_OUTPUT_PREFIX,
    HYPOTHESIS_SETTINGS,
    NPM_PACKAGES,
    stderr_lines,
)
from hypothesis import given
from hypothesis import strategies as st
from reproducible_images_support import (
    DOCKERFILE_PLANS,
    DOCKERFILE_SHAPES,
    installs_npm_dependencies,
    is_conforming,
    offending_packages,
    run_for,
)


@given(plan=DOCKERFILE_PLANS)
@HYPOTHESIS_SETTINGS
def test_reproducible_images_property_passes_only_when_all_conform(
    tmp_path: Path, plan: dict[str, str]
) -> None:
    passed = run_for(tmp_path, plan).returncode == 0

    assert passed is (offending_packages(plan) == set())


@given(plan=DOCKERFILE_PLANS)
@HYPOTHESIS_SETTINGS
def test_reproducible_images_property_prefixes_every_stderr_line(
    tmp_path: Path, plan: dict[str, str]
) -> None:
    for line in stderr_lines(run_for(tmp_path, plan)):
        assert line.startswith(HOOK_OUTPUT_PREFIX)


@given(plan=DOCKERFILE_PLANS)
@HYPOTHESIS_SETTINGS
def test_reproducible_images_property_always_prints_its_rationale(
    tmp_path: Path, plan: dict[str, str]
) -> None:
    assert run_for(tmp_path, plan).stdout.startswith(HOOK_OUTPUT_PREFIX)


@given(plan=DOCKERFILE_PLANS)
@HYPOTHESIS_SETTINGS
def test_reproducible_images_property_names_each_offender(
    tmp_path: Path, plan: dict[str, str]
) -> None:
    finished = run_for(tmp_path, plan)

    for package in offending_packages(plan):
        assert package in finished.stderr


@given(plan=DOCKERFILE_PLANS)
@HYPOTHESIS_SETTINGS
def test_reproducible_images_property_never_names_a_conforming_package(
    tmp_path: Path, plan: dict[str, str]
) -> None:
    finished = run_for(tmp_path, plan)
    offenders = offending_packages(plan)

    for package in set(NPM_PACKAGES) - offenders:
        assert package not in finished.stderr


@given(dockerfile=st.sampled_from(DOCKERFILE_SHAPES))
def test_is_conforming_property_only_judges_an_installing_dockerfile(
    dockerfile: str,
) -> None:
    if not installs_npm_dependencies(dockerfile):
        assert is_conforming(dockerfile)


@given(dockerfile=st.text())
def test_installs_npm_dependencies_property_needs_an_install_marker(
    dockerfile: str,
) -> None:
    detected = installs_npm_dependencies(dockerfile)

    assert detected is ("npm ci" in dockerfile or "install" in dockerfile)


@given(plan=DOCKERFILE_PLANS)
def test_offending_packages_property_is_a_subset_of_the_plan(
    plan: dict[str, str],
) -> None:
    assert offending_packages(plan) <= set(plan)
