#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"

# shellcheck source=lib/shell.sh
source "$ROOT_DIR/scripts/lib/shell.sh"
hla2010_shell_init "$0"

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  cat <<'EOF'
seed_suite.sh: run the default CI quality gate locally.
Evidence:
- upstream_contract.sh
- lint.sh
- test.py
- target_radar_backend_matrix.sh
EOF
  exit 0
fi

run_stage() {
  local stage="$1"
  shift
  local attempt=1
  local max_attempts=2
  while :; do
    if "$@"; then
      return 0
    fi
    status=$?
    if [[ $status -ne 137 || $attempt -ge $max_attempts ]]; then
      return "$status"
    fi
    hla2010_shell_warn "retrying $stage after SIGKILL"
    attempt=$((attempt + 1))
  done
}

run_stage upstream_contract "$ROOT_DIR/scripts/ci/upstream_contract.sh"
run_stage lint "$ROOT_DIR/scripts/ci/lint.sh"
run_stage test "$(command -v python3 || command -v python)" "$ROOT_DIR/scripts/ci/test.py" "$@"
if [[ "${HLA2010_SKIP_TARGET_RADAR_BACKEND_MATRIX:-0}" != "1" ]]; then
  run_stage target_radar_backend_matrix "$ROOT_DIR/scripts/ci/target_radar_backend_matrix.sh"
fi
