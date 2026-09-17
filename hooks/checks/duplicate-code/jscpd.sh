#!/bin/sh
set -e
. "$(dirname "$0")/../../_env.sh"

import_statement='import[^;]*;'

require_binary "$jscpd_binary" jscpd

for package in $services $node_packages; do
    if ! "$jscpd_binary" "$package/src" \
        --threshold 0 \
        --ignore-pattern "$import_statement" \
        --reporters console \
        --silent; then
        echo "pre-commit: duplicated code in $package - reuse it," >&2
        echo "pre-commit: do not copy it" >&2
        exit 1
    fi
done
