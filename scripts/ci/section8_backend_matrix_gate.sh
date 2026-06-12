#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"

# shellcheck source=lib/shell.sh
source "$ROOT_DIR/scripts/lib/shell.sh"
hla2010_shell_init "$0"
PYTHON_BIN="$(hla2010_shell_python_bin)"

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  cat <<'EOF'
section8_backend_matrix_gate.sh: run the cross-backend Section 8 matrix.
Evidence:
- tests/time/test_section8_backend_matrix.py
- analysis/compliance/section8_backend_matrix.{json,md}
EOF
  exit 0
fi

if [[ -f "$ROOT_DIR/.venv/bin/activate" ]]; then
  # shellcheck disable=SC1091
  source "$ROOT_DIR/.venv/bin/activate"
fi

cd "$ROOT_DIR"

hla2010_shell_run_workspace_python "$PYTHON_BIN" -m pytest -q tests/time/test_section8_backend_matrix.py "$@"
hla2010_shell_run_workspace_python "$PYTHON_BIN" scripts/generate_compliance_artifacts.py

printf '%s\n' "updated analysis/compliance/section8_backend_matrix.json"
printf '%s\n' "updated analysis/compliance/section8_backend_matrix.md"
