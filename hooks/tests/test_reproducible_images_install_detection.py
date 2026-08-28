from pathlib import Path

from reproducible_images_support import (
    CONFORMING_DOCKERFILE,
    GATEWAY_PACKAGE,
    UI_PACKAGE,
    run_for,
)

NPM_ALIAS_INSTALL_DOCKERFILE = (
    "FROM node:20-alpine AS builder\n"
    "WORKDIR /build\n"
    "COPY package.json ./\n"
    "RUN npm i\n"
    "COPY src ./src\n"
)
OS_PACKAGE_INSTALL_DOCKERFILE = (
    "FROM nginx:alpine\n"
    "RUN apt-get update && apt-get install -y curl\n"
    "COPY nginx.conf /etc/nginx/nginx.conf\n"
)


def test_r13_an_npm_alias_install_without_a_lockfile_fails(
    tmp_path: Path,
) -> None:
    plan = {
        GATEWAY_PACKAGE: NPM_ALIAS_INSTALL_DOCKERFILE,
        UI_PACKAGE: CONFORMING_DOCKERFILE,
    }
    finished = run_for(tmp_path, plan)

    assert finished.returncode == 1
    assert GATEWAY_PACKAGE in finished.stderr


def test_r15_an_os_package_install_is_not_an_npm_install(
    tmp_path: Path,
) -> None:
    plan = {
        GATEWAY_PACKAGE: OS_PACKAGE_INSTALL_DOCKERFILE,
        UI_PACKAGE: CONFORMING_DOCKERFILE,
    }
    finished = run_for(tmp_path, plan)

    assert finished.returncode == 0
    assert finished.stderr == ""
