#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"

# shellcheck source=lib/shell.sh
source "$ROOT_DIR/scripts/lib/shell.sh"
hla2010_shell_init "$0"

usage() {
  cat <<'EOF'
usage: ./scripts/ci/full_sequence.sh

Run the repo-green full documented local lifecycle sequence:
install -> compilation -> lint / type annotations -> unit tests
-> integration smoke -> integration tests -> compliance matrices
-> full backend matrixed compliance -> other evidence

Blocked vendor prerequisites still run mandatory preflight first and then skip
cleanly. Use ./scripts/ci/vendor_green.sh for strict real-runtime failure.
EOF
}

case "${1:-}" in
  help|-h|--help)
    usage
    exit 0
    ;;
esac

run_step() {
  local label="$1"
  shift
  hla2010_shell_log "$label"
  "$@"
}

run_step "install" "$ROOT_DIR/scripts/ci/install_python.sh"
run_step "compilation" "$ROOT_DIR/scripts/ci/lint.sh"
run_step "lint / type annotations" "$ROOT_DIR/scripts/ci/pyright.sh"
run_step "unit tests" "$ROOT_DIR/scripts/ci/test.sh"
run_step "integration smoke" "$ROOT_DIR/scripts/ci/vendor_runtime_smoke.sh" matrix
python_bin="$(hla2010_shell_python_bin)"
run_step "integration tests" "$python_bin" "$ROOT_DIR/scripts/run_two_federate_suite.py"
run_step "other tests" "$ROOT_DIR/scripts/ci/target_radar_backend_matrix.sh"
run_step "other tests" "$ROOT_DIR/scripts/ci/target_radar_proof.sh"
run_step "HLA-X FOM showcase" "$ROOT_DIR/scripts/ci/hlax_fom_showcase.sh"
run_step "compliance matrices" "$ROOT_DIR/scripts/ci/section8_backend_matrix_gate.sh"
run_step "full backend matrixed compliance" "$ROOT_DIR/scripts/ci/vendor_runtime_smoke.sh" all
