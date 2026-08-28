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

CHECK_NAME = "reproducible-images"
CHECK_SCRIPT = REPOSITORY / "hooks" / "checks" / CHECK_NAME / "check"
GATEWAY_PACKAGE = "api-gateway"
UI_PACKAGE = "ui-service"
FORBIDDEN_INSTALL = "npm install"
LOCKFILE_COPY_LINE = "COPY package.json package-lock.json ./"
PLAIN_COPY_LINE = "COPY package.json ./"
TSCONFIG_COPY_LINE = "COPY tsconfig.json ./"
SOURCE_COPY_LINE = "COPY src ./src"
NPM_CI_LINE = "RUN npm ci"
NPM_INSTALL_LINE = "RUN npm install"
YARN_INSTALL_LINE = "RUN yarn install --frozen-lockfile"
INSTALL_MARKERS = ("npm ci", "install")


def dockerfile_with(*lines: str) -> str:
    body = "\n".join(
        (
            "FROM node:20-alpine AS builder",
            "WORKDIR /build",
            *lines,
            SOURCE_COPY_LINE,
        )
    )

    return f"{body}\n"


CONFORMING_DOCKERFILE = dockerfile_with(LOCKFILE_COPY_LINE, NPM_CI_LINE)
MISSING_LOCKFILE_DOCKERFILE = dockerfile_with(PLAIN_COPY_LINE, NPM_CI_LINE)
NPM_INSTALL_DOCKERFILE = dockerfile_with(
    LOCKFILE_COPY_LINE, NPM_INSTALL_LINE
)
MISSING_NPM_CI_DOCKERFILE = dockerfile_with(
    LOCKFILE_COPY_LINE, YARN_INSTALL_LINE
)
NO_INSTALL_DOCKERFILE = (
    "FROM nginx:alpine\nCOPY nginx.conf /etc/nginx/nginx.conf\n"
)
DOCKERFILE_SHAPES = (
    CONFORMING_DOCKERFILE,
    MISSING_LOCKFILE_DOCKERFILE,
    NPM_INSTALL_DOCKERFILE,
    MISSING_NPM_CI_DOCKERFILE,
    NO_INSTALL_DOCKERFILE,
)
CONFORMING_PLAN = {
    package: CONFORMING_DOCKERFILE for package in NPM_PACKAGES
}
DOCKERFILE_PLANS = st.dictionaries(
    keys=st.sampled_from(NPM_PACKAGES),
    values=st.sampled_from(DOCKERFILE_SHAPES),
)


def installs_npm_dependencies(dockerfile: str) -> bool:
    return any(marker in dockerfile for marker in INSTALL_MARKERS)


def is_conforming(dockerfile: str) -> bool:
    if not installs_npm_dependencies(dockerfile):
        return True

    return (
        "package-lock.json" in dockerfile
        and "npm ci" in dockerfile
        and FORBIDDEN_INSTALL not in dockerfile
    )


def offending_packages(plan: dict[str, str]) -> set[str]:
    return {
        package
        for package, dockerfile in plan.items()
        if not is_conforming(dockerfile)
    }


def fixture_repository(tmp_path: Path, plan: dict[str, str]) -> Path:
    root = Path(tempfile.mkdtemp(dir=tmp_path))
    repository(root)

    for package in NPM_PACKAGES:
        stage_file(root, f"{package}/src/main.ts", "export const a = 1;\n")

    for package, dockerfile in plan.items():
        stage_file(root, f"{package}/Dockerfile", dockerfile)

    return root


def run_for(tmp_path: Path, plan: dict[str, str]) -> CheckRun:
    return run_check(fixture_repository(tmp_path, plan), CHECK_NAME)


def run_with_unreadable_dockerfile(tmp_path: Path) -> CheckRun:
    root = fixture_repository(tmp_path, CONFORMING_PLAN)
    (root / GATEWAY_PACKAGE / "Dockerfile").chmod(0o000)

    return run_check(root, CHECK_NAME)
