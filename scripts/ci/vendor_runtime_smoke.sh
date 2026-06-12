#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
PROFILE="${1:-all}"
PREFLIGHT_ARTIFACT_DIR="${HLA2010_PREFLIGHT_ARTIFACT_DIR:-$ROOT_DIR/analysis/preflight_artifacts}"
VENDOR_PREFLIGHT_STRICT="${HLA2010_VENDOR_PREFLIGHT_STRICT:-0}"
VENDOR_GAP_PROFILE_DIR="${HLA2010_VENDOR_GAP_PROFILE_DIR:-$ROOT_DIR/analysis/vendor_gap_profiles}"
VENV_DIR="${HLA2010_VENV_DIR:-$ROOT_DIR/.venv}"
VENDOR_AUTO_BOOTSTRAP_PYTHON="${HLA2010_VENDOR_AUTO_BOOTSTRAP_PYTHON:-1}"

# shellcheck source=lib/shell.sh
source "$ROOT_DIR/scripts/lib/shell.sh"
hla2010_shell_init "$0"

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  cat <<'EOF'
vendor_runtime_smoke.sh: run CERTI and Pitch runtime smoke/profile checks.
Profiles:
- certi, certi-patched, certi-upstream, certi-compare
- certi-save-restore
- certi-save-restore-probe
- certi-ddm
- certi-ddm-probe
- pitch, pitch-smoke, pitch-verify
- pitch-save-restore
- pitch-save-restore-probe
- pitch-ddm
- pitch-ddm-probe
- pitch-negotiated
- pitch-negotiated-probe
- pitch-lost-federate
- pitch-lost-federate-probe
- matrix
- all
EOF
  exit 0
fi

# shellcheck disable=SC1091
source "$ROOT_DIR/scripts/local_state.sh"

export HLA2010_ENABLE_REAL_RTI_SMOKE=1
export HLA2010_CERTI_PREFLIGHT_OK="${HLA2010_CERTI_PREFLIGHT_OK:-0}"
export HLA2010_PITCH_PREFLIGHT_OK="${HLA2010_PITCH_PREFLIGHT_OK:-0}"

activate_python_env_if_present() {
  if [[ -f "$VENV_DIR/bin/activate" ]]; then
    # shellcheck disable=SC1091
    source "$VENV_DIR/bin/activate"
    return 0
  fi
  return 1
}

python_bin() {
  if [[ -x "$VENV_DIR/bin/python" ]]; then
    printf '%s\n' "$VENV_DIR/bin/python"
    return 0
  fi
  hla2010_shell_python_bin
}

ensure_python_test_env() {
  if activate_python_env_if_present; then
    return 0
  fi

  if [[ "$VENDOR_AUTO_BOOTSTRAP_PYTHON" != "1" ]]; then
    hla2010_shell_die \
      "python test environment is missing at $VENV_DIR; set HLA2010_VENDOR_AUTO_BOOTSTRAP_PYTHON=1 or run ./tools/bootstrap python"
  fi

  hla2010_shell_warn "python test environment missing at $VENV_DIR; bootstrapping repo virtualenv"
  "$ROOT_DIR/scripts/bootstrap_python.sh"
  VENV_DIR="$ROOT_DIR/.venv"
  activate_python_env_if_present || hla2010_shell_die "bootstrap did not produce $VENV_DIR/bin/activate"
}

run_pytest() {
  ensure_python_test_env
  python -m pytest "$@"
}

ensure_preflight_artifact_dir() {
  mkdir -p "$PREFLIGHT_ARTIFACT_DIR"
}

preflight_artifact_path() {
  local vendor="$1"
  printf '%s/%s-preflight.json\n' "$PREFLIGHT_ARTIFACT_DIR" "$vendor"
}

log_preflight_summary() {
  local vendor="$1"
  local artifact_path="$2"
  "$(python_bin)" - "$vendor" "$artifact_path" <<'PY'
import json
import sys
from pathlib import Path

vendor = sys.argv[1]
path = Path(sys.argv[2])
payload = json.loads(path.read_text(encoding="utf-8"))
environment = payload.get("environment", "unknown")
result = payload.get("result", "unknown")
next_step = payload.get("next_step")
if next_step is None:
    next_steps = payload.get("next_steps") or []
    next_step = next_steps[0] if next_steps else None
print(f"[{vendor} preflight] artifact: {path}")
print(f"[{vendor} preflight] environment: {environment}")
print(f"[{vendor} preflight] result: {result}")
if next_step:
    print(f"[{vendor} preflight] next step: {next_step}")
PY
}

handle_blocked_preflight() {
  local vendor="$1"
  local artifact_path="$2"
  local status="$3"
  log_preflight_summary "$vendor" "$artifact_path"
  if [[ "$VENDOR_PREFLIGHT_STRICT" == "1" ]]; then
    hla2010_shell_warn "$vendor preflight blocked in strict mode; failing vendor runtime smoke"
    return "$status"
  fi
  hla2010_shell_warn "$vendor preflight blocked; skipping runtime smoke for this vendor"
  return 2
}

emit_known_gap_profile() {
  local profile="$1"
  mkdir -p "$VENDOR_GAP_PROFILE_DIR"
  local python_bin
  python_bin="$(hla2010_shell_python_bin)"
  "$python_bin" "$ROOT_DIR/scripts/write_vendor_gap_profile.py" \
    --profile "$profile" \
    --output-dir "$VENDOR_GAP_PROFILE_DIR"
}

run_certi_preflight() {
  ensure_preflight_artifact_dir
  local artifact_path
  artifact_path="$(preflight_artifact_path certi)"
  local status=0
  if "$ROOT_DIR/scripts/check_certi_preflight.sh" --json-file "$artifact_path"; then
    log_preflight_summary "certi" "$artifact_path"
    return 0
  else
    status=$?
  fi
  handle_blocked_preflight "certi" "$artifact_path" "$status"
}

run_pitch_preflight() {
  ensure_preflight_artifact_dir
  local artifact_path
  artifact_path="$(preflight_artifact_path pitch)"
  local status=0
  if "$ROOT_DIR/scripts/check_pitch_preflight.sh" --json-file "$artifact_path"; then
    log_preflight_summary "pitch" "$artifact_path"
    return 0
  else
    status=$?
  fi
  handle_blocked_preflight "pitch" "$artifact_path" "$status"
}

guard_vendor_preflight() {
  local vendor="$1"
  local status=0
  case "$vendor" in
    certi)
      if run_certi_preflight; then
        export HLA2010_CERTI_PREFLIGHT_OK=1
        return 0
      else
        status=$?
      fi
      ;;
    pitch)
      if run_pitch_preflight; then
        export HLA2010_PITCH_PREFLIGHT_OK=1
        return 0
      else
        status=$?
      fi
      ;;
    *)
      hla2010_shell_die "unknown vendor preflight guard: $vendor"
      ;;
  esac
  return "$status"
}

default_state_path() {
  local name="$1"
  local path
  path="$(local_state_path "$name")"
  if [[ -e "$path" ]]; then
    printf '%s\n' "$path"
  fi
}

default_pitch_home() {
  if [[ -n "${HLA2010_PITCH_HOME:-}" && -d "${HLA2010_PITCH_HOME:-}" ]]; then
    printf '%s\n' "$HLA2010_PITCH_HOME"
    return 0
  fi
  if [[ -d "$ROOT_DIR/third_party/pitch/PITCH-prti1516e-manual" ]]; then
    printf '%s\n' "$ROOT_DIR/third_party/pitch/PITCH-prti1516e-manual"
    return 0
  fi
  local extracted
  extracted="$ROOT_DIR/third_party/pitch/HLA_PITCH_linux/PITCH-prti1516e-manual"
  if [[ -d "$extracted" ]]; then
    printf '%s\n' "$extracted"
    return 0
  fi
  return 1
}

require_runtime_prefix() {
  local label="$1"
  local path="$2"
  if [[ -z "$path" || ! -x "$path/bin/rtig" ]]; then
    echo "$label is required" >&2
    exit 1
  fi
}

run_certi_patched() {
  hla2010_shell_log "vendor runtime smoke: certi patched"
  if guard_vendor_preflight certi; then
    :
  else
    case "$?" in
      2) return 0 ;;
      *) return $? ;;
    esac
  fi
  export HLA2010_CERTI_PATCHED_PREFIX="${HLA2010_CERTI_PATCHED_PREFIX:-${HLA2010_CERTI_PREFIX:-$(default_state_path "CERTI-install")}}"
  export HLA2010_CERTI_PATCHED_BUILD_ROOT="${HLA2010_CERTI_PATCHED_BUILD_ROOT:-${HLA2010_CERTI_BUILD_ROOT:-$(default_state_path "CERTI-build")}}"
  export HLA2010_CERTI_PREFIX="$HLA2010_CERTI_PATCHED_PREFIX"
  export HLA2010_CERTI_BUILD_ROOT="$HLA2010_CERTI_PATCHED_BUILD_ROOT"
  require_runtime_prefix "patched CERTI install prefix" "${HLA2010_CERTI_PATCHED_PREFIX:-}"
  run_pytest -q tests/vendors/test_real_vendor_runtime_smoke.py -k 'certi'
  run_pytest -q \
    tests/vendors/test_certi_real_backend_exchange_matrix.py \
    tests/vendors/test_certi_real_backend_time_matrix.py \
    tests/vendors/test_certi_real_backend_ownership_matrix.py \
    -k 'not test_certi_upstream_time_query_and_fqr_baseline and not test_certi_patched_negotiated_ownership_baseline'
}

run_certi_upstream() {
  hla2010_shell_log "vendor runtime smoke: certi upstream"
  if guard_vendor_preflight certi; then
    :
  else
    case "$?" in
      2) return 0 ;;
      *) return $? ;;
    esac
  fi
  export HLA2010_CERTI_UPSTREAM_PREFIX="${HLA2010_CERTI_UPSTREAM_PREFIX:-$(default_state_path "CERTI-upstream-install")}"
  export HLA2010_CERTI_UPSTREAM_BUILD_ROOT="${HLA2010_CERTI_UPSTREAM_BUILD_ROOT:-$(default_state_path "CERTI-upstream-build")}"
  require_runtime_prefix "upstream CERTI install prefix" "${HLA2010_CERTI_UPSTREAM_PREFIX:-}"
  run_pytest -q \
    tests/vendors/test_certi_real_backend_time_matrix.py \
    tests/vendors/test_certi_real_backend_ownership_matrix.py \
    -k 'test_certi_upstream_time_query_and_fqr_baseline or test_certi_upstream_queued_fqr_baseline or test_certi_upstream_negotiated_ownership_baseline or test_certi_upstream_release_request_branch_baseline'
}

run_certi_compare() {
  hla2010_shell_log "vendor runtime smoke: certi compare"
  if guard_vendor_preflight certi; then
    :
  else
    case "$?" in
      2) return 0 ;;
      *) return $? ;;
    esac
  fi
  export HLA2010_CERTI_UPSTREAM_PREFIX="${HLA2010_CERTI_UPSTREAM_PREFIX:-$(default_state_path "CERTI-upstream-install")}"
  export HLA2010_CERTI_UPSTREAM_BUILD_ROOT="${HLA2010_CERTI_UPSTREAM_BUILD_ROOT:-$(default_state_path "CERTI-upstream-build")}"
  export HLA2010_CERTI_PATCHED_PREFIX="${HLA2010_CERTI_PATCHED_PREFIX:-${HLA2010_CERTI_PREFIX:-$(default_state_path "CERTI-install")}}"
  export HLA2010_CERTI_PATCHED_BUILD_ROOT="${HLA2010_CERTI_PATCHED_BUILD_ROOT:-${HLA2010_CERTI_BUILD_ROOT:-$(default_state_path "CERTI-build")}}"
  require_runtime_prefix "upstream CERTI install prefix" "${HLA2010_CERTI_UPSTREAM_PREFIX:-}"
  require_runtime_prefix "patched CERTI install prefix" "${HLA2010_CERTI_PATCHED_PREFIX:-}"
  run_pytest -q \
    tests/vendors/test_certi_real_backend_time_matrix.py \
    tests/vendors/test_certi_real_backend_ownership_matrix.py \
    -k 'test_certi_upstream_time_query_and_fqr_baseline or test_certi_patched_time_query_and_fqr_baseline or test_certi_upstream_queued_fqr_baseline or test_certi_patched_queued_fqr_baseline or test_certi_upstream_negotiated_ownership_baseline or test_certi_upstream_release_request_branch_baseline or test_certi_patched_release_request_branch_baseline'
}

case "$PROFILE" in
  certi)
    run_certi_patched
    ;;
  certi-patched)
    run_certi_patched
    ;;
  certi-upstream)
    run_certi_upstream
    ;;
  certi-compare)
    run_certi_compare
    ;;
  certi-save-restore)
    hla2010_shell_log "vendor runtime profile: certi save/restore"
    if guard_vendor_preflight certi; then
      :
    else
      case "$?" in
        2) exit 0 ;;
        *) exit $? ;;
      esac
    fi
    emit_known_gap_profile "certi-save-restore"
    hla2010_shell_warn "CERTI real-runtime save/restore remains a known unpromoted gap in this workspace"
    exit 3
    ;;
  certi-save-restore-probe)
    hla2010_shell_log "vendor runtime profile: certi save/restore probe"
    if guard_vendor_preflight certi; then
      :
    else
      case "$?" in
        2) exit 0 ;;
        *) exit $? ;;
      esac
    fi
    export HLA2010_CERTI_PATCHED_PREFIX="${HLA2010_CERTI_PATCHED_PREFIX:-${HLA2010_CERTI_PREFIX:-$(default_state_path "CERTI-install")}}"
    export HLA2010_CERTI_PATCHED_BUILD_ROOT="${HLA2010_CERTI_PATCHED_BUILD_ROOT:-${HLA2010_CERTI_BUILD_ROOT:-$(default_state_path "CERTI-build")}}"
    export HLA2010_CERTI_PREFIX="$HLA2010_CERTI_PATCHED_PREFIX"
    export HLA2010_CERTI_BUILD_ROOT="$HLA2010_CERTI_PATCHED_BUILD_ROOT"
    require_runtime_prefix "patched CERTI install prefix" "${HLA2010_CERTI_PATCHED_PREFIX:-}"
    run_pytest -q tests/vendors/test_real_vendor_runtime_smoke.py -k 'certi_real_save_restore_smoke'
    ;;
  certi-ddm)
    hla2010_shell_log "vendor runtime profile: certi DDM"
    if guard_vendor_preflight certi; then
      :
    else
      case "$?" in
        2) exit 0 ;;
        *) exit $? ;;
      esac
    fi
    emit_known_gap_profile "certi-ddm"
    hla2010_shell_warn "CERTI real-runtime DDM remains a known unpromoted gap in this workspace"
    exit 3
    ;;
  certi-ddm-probe)
    hla2010_shell_log "vendor runtime profile: certi DDM probe"
    if guard_vendor_preflight certi; then
      :
    else
      case "$?" in
        2) exit 0 ;;
        *) exit $? ;;
      esac
    fi
    export HLA2010_CERTI_PATCHED_PREFIX="${HLA2010_CERTI_PATCHED_PREFIX:-${HLA2010_CERTI_PREFIX:-$(default_state_path "CERTI-install")}}"
    export HLA2010_CERTI_PATCHED_BUILD_ROOT="${HLA2010_CERTI_PATCHED_BUILD_ROOT:-${HLA2010_CERTI_BUILD_ROOT:-$(default_state_path "CERTI-build")}}"
    export HLA2010_CERTI_PREFIX="$HLA2010_CERTI_PATCHED_PREFIX"
    export HLA2010_CERTI_BUILD_ROOT="$HLA2010_CERTI_PATCHED_BUILD_ROOT"
    require_runtime_prefix "patched CERTI install prefix" "${HLA2010_CERTI_PATCHED_PREFIX:-}"
    run_pytest -q tests/vendors/test_real_vendor_runtime_smoke.py -k 'certi_real_ddm_smoke'
    ;;
  pitch|pitch-verify|pitch-smoke)
    hla2010_shell_log "vendor runtime smoke: pitch"
    if guard_vendor_preflight pitch; then
      :
    else
      case "$?" in
        2) exit 0 ;;
        *) exit $? ;;
      esac
    fi
    export HLA2010_PITCH_HOME="${HLA2010_PITCH_HOME:-$(default_pitch_home)}"
    test -n "${HLA2010_PITCH_HOME:-}" || { echo "Pitch runtime bundle is required"; exit 1; }
    export HLA2010_PITCH_USER_HOME="${HLA2010_PITCH_USER_HOME:-$("$ROOT_DIR/scripts/setup_pitch_state.sh")}"
    export HLA2010_PITCH_CRC_MODE="${HLA2010_PITCH_CRC_MODE:-docker}"
    export HLA2010_PITCH_DOCKER_BUILD="${HLA2010_PITCH_DOCKER_BUILD:-0}"
    if [[ "$PROFILE" == "pitch-smoke" || "$PROFILE" == "pitch" ]]; then
      # Pitch smoke is the promoted overlap only. Save/restore and DDM remain
      # explicit gap/probe routes, not part of the default smoke contract.
      run_pytest -q tests/vendors/test_real_vendor_runtime_smoke.py -k 'pitch_java_real_lifecycle_smoke or pitch_java_real_exchange_smoke'
    fi
    if [[ "$PROFILE" == "pitch-verify" || "$PROFILE" == "pitch" ]]; then
      run_pytest -q tests/vendors/test_pitch_real_backend_matrix.py
    fi
    ;;
  pitch-save-restore)
    hla2010_shell_log "vendor runtime profile: pitch save/restore"
    if guard_vendor_preflight pitch; then
      :
    else
      case "$?" in
        2) exit 0 ;;
        *) exit $? ;;
      esac
    fi
    emit_known_gap_profile "pitch-save-restore"
    hla2010_shell_warn "Pitch real-runtime save/restore remains a known unpromoted gap in this workspace"
    exit 3
    ;;
  pitch-save-restore-probe)
    hla2010_shell_log "vendor runtime profile: pitch save/restore probe"
    if guard_vendor_preflight pitch; then
      :
    else
      case "$?" in
        2) exit 0 ;;
        *) exit $? ;;
      esac
    fi
    export HLA2010_PITCH_HOME="${HLA2010_PITCH_HOME:-$(default_pitch_home)}"
    test -n "${HLA2010_PITCH_HOME:-}" || { echo "Pitch runtime bundle is required"; exit 1; }
    export HLA2010_PITCH_USER_HOME="${HLA2010_PITCH_USER_HOME:-$("$ROOT_DIR/scripts/setup_pitch_state.sh")}"
    export HLA2010_PITCH_CRC_MODE="${HLA2010_PITCH_CRC_MODE:-docker}"
    export HLA2010_PITCH_DOCKER_BUILD="${HLA2010_PITCH_DOCKER_BUILD:-0}"
    run_pytest -q tests/vendors/test_real_vendor_runtime_smoke.py -k 'pitch_java_real_save_restore_smoke'
    ;;
  pitch-ddm)
    hla2010_shell_log "vendor runtime profile: pitch DDM"
    if guard_vendor_preflight pitch; then
      :
    else
      case "$?" in
        2) exit 0 ;;
        *) exit $? ;;
      esac
    fi
    emit_known_gap_profile "pitch-ddm"
    hla2010_shell_warn "Pitch real-runtime DDM remains a known unpromoted gap in this workspace"
    exit 3
    ;;
  pitch-ddm-probe)
    hla2010_shell_log "vendor runtime profile: pitch DDM probe"
    if guard_vendor_preflight pitch; then
      :
    else
      case "$?" in
        2) exit 0 ;;
        *) exit $? ;;
      esac
    fi
    export HLA2010_PITCH_HOME="${HLA2010_PITCH_HOME:-$(default_pitch_home)}"
    test -n "${HLA2010_PITCH_HOME:-}" || { echo "Pitch runtime bundle is required"; exit 1; }
    export HLA2010_PITCH_USER_HOME="${HLA2010_PITCH_USER_HOME:-$("$ROOT_DIR/scripts/setup_pitch_state.sh")}"
    export HLA2010_PITCH_CRC_MODE="${HLA2010_PITCH_CRC_MODE:-docker}"
    export HLA2010_PITCH_DOCKER_BUILD="${HLA2010_PITCH_DOCKER_BUILD:-0}"
    run_pytest -q tests/vendors/test_real_vendor_runtime_smoke.py -k 'pitch_java_real_ddm_smoke'
    ;;
  pitch-negotiated)
    hla2010_shell_log "vendor runtime profile: pitch negotiated ownership"
    if guard_vendor_preflight pitch; then
      :
    else
      case "$?" in
        2) exit 0 ;;
        *) exit $? ;;
      esac
    fi
    emit_known_gap_profile "pitch-negotiated"
    hla2010_shell_warn "Pitch real-runtime negotiated ownership remains a known bridge-divergent unpromoted gap in this workspace"
    exit 3
    ;;
  pitch-negotiated-probe)
    hla2010_shell_log "vendor runtime profile: pitch negotiated ownership probe"
    if guard_vendor_preflight pitch; then
      :
    else
      case "$?" in
        2) exit 0 ;;
        *) exit $? ;;
      esac
    fi
    export HLA2010_PITCH_HOME="${HLA2010_PITCH_HOME:-$(default_pitch_home)}"
    test -n "${HLA2010_PITCH_HOME:-}" || { echo "Pitch runtime bundle is required"; exit 1; }
    export HLA2010_PITCH_USER_HOME="${HLA2010_PITCH_USER_HOME:-$("$ROOT_DIR/scripts/setup_pitch_state.sh")}"
    export HLA2010_PITCH_CRC_MODE="${HLA2010_PITCH_CRC_MODE:-docker}"
    export HLA2010_PITCH_DOCKER_BUILD="${HLA2010_PITCH_DOCKER_BUILD:-0}"
    run_pytest -q tests/vendors/test_pitch_real_backend_matrix.py -k 'pitch_negotiated_divesting_offer_probe or pitch_release_request_owned_attribute_probe'
    ;;
  pitch-lost-federate)
    hla2010_shell_log "vendor runtime profile: pitch lost federate"
    if guard_vendor_preflight pitch; then
      :
    else
      case "$?" in
        2) exit 0 ;;
        *) exit $? ;;
      esac
    fi
    emit_known_gap_profile "pitch-lost-federate"
    hla2010_shell_warn "Pitch real-runtime lost-federate parity remains blocked at the family level; use the JPype/Py4J probe route to gather promotion evidence"
    exit 3
    ;;
  pitch-lost-federate-probe)
    hla2010_shell_log "vendor runtime profile: pitch lost federate probe"
    if guard_vendor_preflight pitch; then
      :
    else
      case "$?" in
        2) exit 0 ;;
        *) exit $? ;;
      esac
    fi
    export HLA2010_PITCH_HOME="${HLA2010_PITCH_HOME:-$(default_pitch_home)}"
    test -n "${HLA2010_PITCH_HOME:-}" || { echo "Pitch runtime bundle is required"; exit 1; }
    export HLA2010_PITCH_CRC_HEARTBEAT_ENABLE="${HLA2010_PITCH_CRC_HEARTBEAT_ENABLE:-true}"
    export HLA2010_PITCH_CRC_HEARTBEAT_INTERVAL="${HLA2010_PITCH_CRC_HEARTBEAT_INTERVAL:-1}"
    export HLA2010_PITCH_CRC_HEARTBEAT_ACTION="${HLA2010_PITCH_CRC_HEARTBEAT_ACTION:-resign}"
    export HLA2010_PITCH_LRC_PEER_HEARTBEAT_INTERVAL_MILLIS="${HLA2010_PITCH_LRC_PEER_HEARTBEAT_INTERVAL_MILLIS:-1000}"
    export HLA2010_PITCH_FEDPRO_TIMEOUT_HEART_SECONDS="${HLA2010_PITCH_FEDPRO_TIMEOUT_HEART_SECONDS:-5}"
    export HLA2010_PITCH_FEDPRO_TIMEOUT_PURGE_SECONDS="${HLA2010_PITCH_FEDPRO_TIMEOUT_PURGE_SECONDS:-15}"
    export HLA2010_PITCH_USER_HOME="${HLA2010_PITCH_USER_HOME:-$("$ROOT_DIR/scripts/setup_pitch_state.sh")}"
    export HLA2010_PITCH_CRC_MODE="${HLA2010_PITCH_CRC_MODE:-docker}"
    export HLA2010_PITCH_DOCKER_BUILD="${HLA2010_PITCH_DOCKER_BUILD:-0}"
    run_pytest -q tests/vendors/test_pitch_real_backend_matrix.py -k 'pitch_backend_lost_federate_mom_matrix'
    ;;
  matrix)
    hla2010_shell_log "vendor runtime smoke: matrix"
    "$0" certi
    "$0" pitch
    ;;
  all)
    hla2010_shell_log "vendor runtime smoke: all"
    certi_ready=0
    pitch_ready=0
    if guard_vendor_preflight certi; then
      certi_ready=1
    else
      case "$?" in
        2) certi_ready=0 ;;
        *) exit $? ;;
      esac
    fi
    if guard_vendor_preflight pitch; then
      pitch_ready=1
    else
      case "$?" in
        2) pitch_ready=0 ;;
        *) exit $? ;;
      esac
    fi
    if [[ "$certi_ready" -eq 0 && "$pitch_ready" -eq 0 ]]; then
      hla2010_shell_warn "no runnable vendor runtime remained after preflight; skipping smoke file"
      exit 0
    fi
    if [[ "$certi_ready" -eq 1 && "$pitch_ready" -eq 1 ]]; then
      run_pytest -q tests/vendors/test_real_vendor_runtime_smoke.py
    elif [[ "$certi_ready" -eq 1 ]]; then
      run_pytest -q tests/vendors/test_real_vendor_runtime_smoke.py -k 'certi'
    else
      export HLA2010_PITCH_HOME="${HLA2010_PITCH_HOME:-$(default_pitch_home)}"
      export HLA2010_PITCH_USER_HOME="${HLA2010_PITCH_USER_HOME:-$("$ROOT_DIR/scripts/setup_pitch_state.sh")}"
      export HLA2010_PITCH_CRC_MODE="${HLA2010_PITCH_CRC_MODE:-docker}"
      export HLA2010_PITCH_DOCKER_BUILD="${HLA2010_PITCH_DOCKER_BUILD:-0}"
      run_pytest -q tests/vendors/test_real_vendor_runtime_smoke.py -k 'pitch'
    fi
    ;;
  *)
    echo "usage: $0 [certi|certi-patched|certi-upstream|certi-compare|certi-save-restore|certi-save-restore-probe|certi-ddm|certi-ddm-probe|pitch|pitch-smoke|pitch-verify|pitch-save-restore|pitch-save-restore-probe|pitch-ddm|pitch-ddm-probe|pitch-negotiated|pitch-negotiated-probe|pitch-lost-federate|pitch-lost-federate-probe|matrix|all]" >&2
    exit 2
    ;;
esac
