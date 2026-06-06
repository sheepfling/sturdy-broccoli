#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"

# shellcheck disable=SC1091
source "$ROOT_DIR/.venv/bin/activate"

ruff check scripts/ci

COMPILE_TARGETS=()
for target in hla2010 tests tools; do
    if [ -d "$ROOT_DIR/$target" ] && find "$ROOT_DIR/$target" -name '*.py' -print -quit | grep -q .; then
        COMPILE_TARGETS+=("$target")
    fi
done

python -m compileall -q "${COMPILE_TARGETS[@]}"
