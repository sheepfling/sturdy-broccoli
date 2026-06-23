#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"

# shellcheck source=lib/shell.sh
source "$ROOT_DIR/scripts/lib/shell.sh"
hla2010_shell_init "$0"

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  cat <<'EOF'
test.sh: run pytest for the full suite or the selected paths.
Evidence:
- python -m pytest -q
EOF
  exit 0
fi

PYTHON_BIN="$(hla2010_shell_python_bin)"

if [[ "$#" -eq 0 ]]; then
  "$PYTHON_BIN" -m pytest -q
else
  "$PYTHON_BIN" -m pytest -q "$@"
fi
