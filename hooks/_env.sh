repository_root=$(git rev-parse --show-toplevel)
cd "$repository_root"

declared_services="user-service content-management-service"
declared_node_packages="ui-service api-gateway"

services=""
node_packages=""

for declared in $declared_services; do
    if [ -d "$declared/src" ]; then
        services="$services $declared"
    fi
done

for declared in $declared_node_packages; do
    if [ -d "$declared/src" ]; then
        node_packages="$node_packages $declared"
    fi
done

ruff_binary="$repository_root/.venv/bin/ruff"
basedpyright_binary="$repository_root/.venv/bin/basedpyright"
pylint_binary="$repository_root/.venv/bin/pylint"
vulture_binary="$repository_root/.venv/bin/vulture"
deptry_binary="$repository_root/.venv/bin/deptry"
python_binary="$repository_root/.venv/bin/python"
pip_audit_binary="$repository_root/.venv/bin/pip-audit"
semgrep_binary="$repository_root/.venv/bin/semgrep"

node_binary=$(command -v node || true)
eslint_binary="$repository_root/hooks/node_modules/.bin/eslint"
jscpd_binary="$repository_root/hooks/node_modules/.bin/jscpd"
knip_binary="$repository_root/hooks/node_modules/.bin/knip"
typescript_module="$repository_root/hooks/node_modules/typescript"

source_directories=""
test_directories=""

for service in $services; do
    source_directories="$source_directories $service/src"
    test_directories="$test_directories $service/tests"
done

node_source_directories=""

for node_package in $node_packages; do
    node_source_directories="$node_source_directories $node_package/src"
done

require_binary() {
    if [ ! -x "$1" ]; then
        echo "pre-commit: $2 is not installed - run ./install.sh" >&2
        exit 1
    fi
}

require_node_modules() {
    if [ ! -d "$1/node_modules" ]; then
        echo "pre-commit: $1 has no node_modules - run ./install.sh" >&2
        exit 1
    fi
}

python_files_in() {
    find "$@" \
        -name __pycache__ -prune -o \
        -name node_modules -prune -o \
        -type f -name '*.py' -print \
        | sed 's|^\./||' \
        | sort
}

typescript_files_in() {
    find "$@" \
        -name node_modules -prune -o \
        -name dist -prune -o \
        -type f \( -name '*.ts' -o -name '*.tsx' \) -print \
        | sed 's|^\./||' \
        | sort
}
