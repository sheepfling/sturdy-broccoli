#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"

# shellcheck source=lib/shell.sh
source "$ROOT_DIR/scripts/lib/shell.sh"

PYTHON_BIN="$(hla2010_shell_python_bin)"
exec "$PYTHON_BIN" "$ROOT_DIR/scripts/ci/test.py" "$@"
