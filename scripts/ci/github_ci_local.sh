#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"

# shellcheck source=../lib/shell.sh
source "$ROOT_DIR/scripts/lib/shell.sh"
hla2010_shell_init "$0"

usage() {
  cat <<'EOF'
usage: ./scripts/ci/github_ci_local.sh [mode]

Run GitHub CI lanes locally with stable top-to-bottom ordering.

Modes:
- default: lightweight contract guard plus the default GitHub Ubuntu stack
- vendor-required: dedicated real-runtime required lanes (certi, pitch, matrix)
- vendor-edge: dedicated vendor-edge matrix lanes
- probe-review: dedicated repeated-run probe review lanes
- vendor-smoke: explicit vendor-runtime-smoke workflow lanes
- all: run every mode above in workflow order

Examples:
  ./scripts/ci/github_ci_local.sh
  ./scripts/ci/github_ci_local.sh vendor-required
  ./scripts/ci/github_ci_local.sh all

Notes:
- default mirrors the repo's default GitHub Actions Ubuntu jobs.
- the vendor-* modes are strict local reruns for machines with the real-runtime
  prerequisites already configured.
- each lane may be overridden for tests via
  HLA2010_GITHUB_CI_LOCAL_<LANE_NAME>_CMD.
EOF
}

mode="${1:-default}"
case "$mode" in
  help|-h|--help)
    usage
    exit 0
    ;;
  default|vendor-required|vendor-edge|probe-review|vendor-smoke|all)
    ;;
  *)
    usage >&2
    exit 2
    ;;
esac

run_lane() {
  local name="$1"
  local override_var="$2"
  shift 2

  hla2010_shell_log "running $name"
  if [[ -n "${!override_var:-}" ]]; then
    bash -lc "${!override_var}"
    return 0
  fi
  "$@"
}

lane_override_var() {
  local lane="$1"
  lane="${lane//-/_}"
  lane="$(printf '%s' "$lane" | tr '[:lower:]' '[:upper:]')"
  printf 'HLA2010_GITHUB_CI_LOCAL_%s_CMD\n' "$lane"
}

run_default_mode() {
  run_lane vendor_runner_contract \
    HLA2010_GITHUB_CI_LOCAL_VENDOR_RUNNER_CONTRACT_CMD \
    python3 "$ROOT_DIR/scripts/check_vendor_runner_template_drift.py"
  run_lane install_python \
    HLA2010_GITHUB_CI_LOCAL_INSTALL_PYTHON_CMD \
    bash "$ROOT_DIR/scripts/ci/install_python.sh"
  run_lane repo_green \
    HLA2010_GITHUB_CI_LOCAL_REPO_GREEN_CMD \
    env HLA2010_SKIP_TARGET_RADAR_BACKEND_MATRIX=1 bash "$ROOT_DIR/scripts/ci/repo_green.sh"
  run_lane seed_suite \
    HLA2010_GITHUB_CI_LOCAL_SEED_SUITE_CMD \
    env HLA2010_SKIP_TARGET_RADAR_BACKEND_MATRIX=1 bash "$ROOT_DIR/scripts/ci/seed_suite.sh"
  run_lane optional_java_bridges \
    HLA2010_GITHUB_CI_LOCAL_OPTIONAL_JAVA_BRIDGES_CMD \
    bash "$ROOT_DIR/scripts/ci/test.sh" tests/runtime/test_optional_real_java_bridges.py
  run_lane target_radar_backend_matrix \
    HLA2010_GITHUB_CI_LOCAL_TARGET_RADAR_BACKEND_MATRIX_CMD \
    bash "$ROOT_DIR/scripts/ci/target_radar_backend_matrix.sh"
  run_lane target_radar_proof \
    HLA2010_GITHUB_CI_LOCAL_TARGET_RADAR_PROOF_CMD \
    bash "$ROOT_DIR/scripts/ci/target_radar_proof.sh"
}

run_vendor_required_mode() {
  run_lane install_python \
    HLA2010_GITHUB_CI_LOCAL_INSTALL_PYTHON_CMD \
    bash "$ROOT_DIR/scripts/ci/install_python.sh"
  run_lane certi_runtime_required \
    HLA2010_GITHUB_CI_LOCAL_CERTI_RUNTIME_REQUIRED_CMD \
    bash -lc "python3 '$ROOT_DIR/scripts/ci/check_vendor_runtime_ci_state.py' --profile certi && bash '$ROOT_DIR/scripts/ci/vendor_green.sh' certi"
  run_lane pitch_runtime_required \
    HLA2010_GITHUB_CI_LOCAL_PITCH_RUNTIME_REQUIRED_CMD \
    bash -lc "python3 '$ROOT_DIR/scripts/ci/check_vendor_runtime_ci_state.py' --profile pitch && bash '$ROOT_DIR/scripts/ci/vendor_green.sh' pitch"
  run_lane real_profile_matrix_required \
    HLA2010_GITHUB_CI_LOCAL_REAL_PROFILE_MATRIX_REQUIRED_CMD \
    bash -lc "python3 '$ROOT_DIR/scripts/ci/check_vendor_runtime_ci_state.py' --profile matrix && bash '$ROOT_DIR/scripts/ci/vendor_green.sh' matrix"
}

run_vendor_edge_mode() {
  local profile
  run_lane install_python \
    HLA2010_GITHUB_CI_LOCAL_INSTALL_PYTHON_CMD \
    bash "$ROOT_DIR/scripts/ci/install_python.sh"
  run_lane vendor_edge_matrix_validate \
    HLA2010_GITHUB_CI_LOCAL_VENDOR_EDGE_MATRIX_VALIDATE_CMD \
    python3 "$ROOT_DIR/scripts/ci/check_vendor_runtime_ci_state.py" --profile vendor-edge
  for profile in time-query negotiated-ownership save-restore ddm; do
    run_lane "vendor_edge_${profile}" \
      "$(lane_override_var "VENDOR_EDGE_${profile}")" \
      bash "$ROOT_DIR/scripts/ci/vendor_edge_matrix.sh" "$profile"
  done
}

run_probe_review_mode() {
  local profile
  run_lane install_python \
    HLA2010_GITHUB_CI_LOCAL_INSTALL_PYTHON_CMD \
    bash "$ROOT_DIR/scripts/ci/install_python.sh"
  run_lane vendor_probe_review_validate \
    HLA2010_GITHUB_CI_LOCAL_VENDOR_PROBE_REVIEW_VALIDATE_CMD \
    python3 "$ROOT_DIR/scripts/ci/check_vendor_runtime_ci_state.py" --profile vendor-edge
  for profile in \
    certi-save-restore-probe \
    certi-ddm-probe \
    pitch-save-restore-probe \
    pitch-ddm-probe \
    pitch-negotiated-probe \
    pitch-time-window-probe \
    pitch-time-window-restore-state-probe \
    pitch-lost-federate-probe
  do
    run_lane "probe_review_${profile}" \
      "$(lane_override_var "PROBE_REVIEW_${profile}")" \
      bash "$ROOT_DIR/scripts/ci/vendor_probe_review.sh" "$profile" 5
  done
}

run_vendor_smoke_mode() {
  local entry profile command
  run_lane install_python \
    HLA2010_GITHUB_CI_LOCAL_INSTALL_PYTHON_CMD \
    bash "$ROOT_DIR/scripts/ci/install_python.sh"
  for entry in \
    "all all bash $ROOT_DIR/scripts/ci/vendor_green.sh all" \
    "certi-save-restore-probe certi $ROOT_DIR/tools/certi-easy save-restore-probe" \
    "certi-ddm-probe certi $ROOT_DIR/tools/certi-easy ddm-probe" \
    "pitch-save-restore-probe pitch $ROOT_DIR/tools/pitch save-restore-probe" \
    "pitch-ddm-probe pitch $ROOT_DIR/tools/pitch ddm-probe" \
    "pitch-negotiated-probe pitch $ROOT_DIR/tools/pitch negotiated-probe" \
    "pitch-time-window-probe pitch $ROOT_DIR/tools/pitch time-window-probe" \
    "pitch-time-window-restore-state-probe pitch $ROOT_DIR/tools/pitch time-window-restore-state-probe" \
    "pitch-lost-federate-probe pitch $ROOT_DIR/tools/pitch lost-federate-probe"
  do
    read -r name profile command_args <<<"$entry"
    run_lane "vendor_smoke_validate_${name}" \
      "$(lane_override_var "VENDOR_SMOKE_VALIDATE_${name}")" \
      python3 "$ROOT_DIR/scripts/ci/check_vendor_runtime_ci_state.py" --profile "$profile"
    # shellcheck disable=SC2086
    run_lane "vendor_smoke_${name}" \
      "$(lane_override_var "VENDOR_SMOKE_${name}")" \
      $command_args
  done
}

case "$mode" in
  default)
    run_default_mode
    ;;
  vendor-required)
    run_vendor_required_mode
    ;;
  vendor-edge)
    run_vendor_edge_mode
    ;;
  probe-review)
    run_probe_review_mode
    ;;
  vendor-smoke)
    run_vendor_smoke_mode
    ;;
  all)
    run_default_mode
    run_vendor_required_mode
    run_vendor_edge_mode
    run_probe_review_mode
    run_vendor_smoke_mode
    ;;
esac
