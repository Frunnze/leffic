repository_root=$(git rev-parse --show-toplevel)
cd "$repository_root"

services="user-service content-management-service"

ruff_binary="$repository_root/.venv/bin/ruff"
basedpyright_binary="$repository_root/.venv/bin/basedpyright"
mutmut_binary="$repository_root/.venv/bin/mutmut"
pylint_binary="$repository_root/.venv/bin/pylint"
vulture_binary="$repository_root/.venv/bin/vulture"
deptry_binary="$repository_root/.venv/bin/deptry"
python_binary="$repository_root/.venv/bin/python"

require_binary() {
    if [ ! -x "$1" ]; then
        echo "pre-commit: $2 is not installed - run ./install.sh" >&2
        exit 1
    fi
}
