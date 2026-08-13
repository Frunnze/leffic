#!/bin/sh
set -e

repository_root=$(cd "$(dirname "$0")" && pwd)
cd "$repository_root"

virtual_environment=".venv"

if [ ! -d "$virtual_environment" ]; then
    python3 -m venv "$virtual_environment"
fi

"$virtual_environment/bin/pip" install --upgrade pip
"$virtual_environment/bin/pip" install -r requirements-dev.txt
"$virtual_environment/bin/pip" install \
    -r content-management-service/requirements.txt
"$virtual_environment/bin/pip" install -r user-service/requirements.txt

git config core.hooksPath hooks

echo "install: ready - hooks run from $repository_root/hooks"
