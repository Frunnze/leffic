repository_root=$(git rev-parse --show-toplevel)
cd "$repository_root"

services="user-service content-management-service"
node_packages="ui-service api-gateway"

ruff_binary="$repository_root/.venv/bin/ruff"
basedpyright_binary="$repository_root/.venv/bin/basedpyright"
mutmut_binary="$repository_root/.venv/bin/mutmut"
pylint_binary="$repository_root/.venv/bin/pylint"
vulture_binary="$repository_root/.venv/bin/vulture"
deptry_binary="$repository_root/.venv/bin/deptry"
python_binary="$repository_root/.venv/bin/python"
pip_audit_binary="$repository_root/.venv/bin/pip-audit"

source_directories=""
test_directories=""

for service in $services; do
    source_directories="$source_directories $service/src"
    test_directories="$test_directories $service/tests"
done

require_binary() {
    if [ ! -x "$1" ]; then
        echo "pre-commit: $2 is not installed - run ./install.sh" >&2
        exit 1
    fi
}

python_files_in() {
    find "$@" \
        -name __pycache__ -prune -o \
        -name mutants -prune -o \
        -type f -name '*.py' -print \
        | sed 's|^\./||' \
        | sort
}
