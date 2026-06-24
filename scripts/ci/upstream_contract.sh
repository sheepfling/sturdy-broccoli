#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"

# shellcheck source=../lib/shell.sh
source "$ROOT_DIR/scripts/lib/shell.sh"
hla2010_shell_init "$0"

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  cat <<'EOF'
upstream_contract.sh: validate the frozen anonymous upstream contract snapshot.
Evidence:
- checked-in contract snapshot metadata
- local ambassador protocol shape
- local enums and exception hierarchy
- local datatypes and handles
- local time, logical-time, encoding, handle-factory, and RTI-factory support
- import/package boundary guardrails
EOF
  exit 0
fi

PYTHON_BIN="$(hla2010_shell_python_bin)"

"$PYTHON_BIN" "$ROOT_DIR/scripts/check_upstream_contract.py" \
  --check-local-ambassadors \
  --check-local-enums-exceptions \
  --check-local-datatypes-handles \
  --check-local-standard-support

"$PYTHON_BIN" -m pytest -q "$ROOT_DIR/tests/compat"
