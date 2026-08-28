import pytest
from check_support import REPOSITORY, dockerignore_patterns
from gateway_dockerfile_facts import (
    GATEWAY_BASE_IMAGES,
    GATEWAY_CONTEXT_PATHS,
    GATEWAY_NJS_COPY,
    gateway_dockerfile_lines,
    real_dockerfile,
)
from reproducible_images_support import (
    FORBIDDEN_INSTALL,
    GATEWAY_PACKAGE,
    LOCKFILE_COPY_LINE,
    NPM_CI_LINE,
    SOURCE_COPY_LINE,
    TSCONFIG_COPY_LINE,
)


def test_r1_the_lockfile_is_copied_above_the_install_line() -> None:
    lines = gateway_dockerfile_lines()

    assert LOCKFILE_COPY_LINE in lines
    assert NPM_CI_LINE in lines
    assert lines.index(LOCKFILE_COPY_LINE) < lines.index(NPM_CI_LINE)


def test_r2_the_builder_installs_with_plain_npm_ci() -> None:
    assert NPM_CI_LINE in gateway_dockerfile_lines()


def test_r3_the_builder_never_runs_npm_install() -> None:
    assert FORBIDDEN_INSTALL not in real_dockerfile(GATEWAY_PACKAGE)


def test_r4_sources_are_copied_after_the_install_step() -> None:
    lines = gateway_dockerfile_lines()

    assert NPM_CI_LINE in lines

    install_position = lines.index(NPM_CI_LINE)

    assert lines.index(TSCONFIG_COPY_LINE) > install_position
    assert lines.index(SOURCE_COPY_LINE) > install_position


def test_r5_both_base_images_stay_unpinned_by_digest() -> None:
    lines = gateway_dockerfile_lines()
    declared = [line for line in lines if line.startswith("FROM ")]

    assert tuple(declared) == GATEWAY_BASE_IMAGES


def test_r6_the_built_bundle_still_lands_in_the_njs_directory() -> None:
    assert GATEWAY_NJS_COPY in gateway_dockerfile_lines()


@pytest.mark.parametrize("context_path", GATEWAY_CONTEXT_PATHS)
def test_r7_the_build_context_holds_every_copied_path(
    context_path: str,
) -> None:
    assert (REPOSITORY / GATEWAY_PACKAGE / context_path).exists()


@pytest.mark.parametrize("context_path", GATEWAY_CONTEXT_PATHS)
def test_r8_the_dockerignore_excludes_nothing_the_build_copies(
    context_path: str,
) -> None:
    assert context_path not in dockerignore_patterns(GATEWAY_PACKAGE)
