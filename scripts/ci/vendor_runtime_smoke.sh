#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
PROFILE="${1:-all}"

# shellcheck disable=SC1091
source "$ROOT_DIR/scripts/local_state.sh"
# shellcheck disable=SC1091
source "$ROOT_DIR/.venv/bin/activate"

export HLA2010_ENABLE_REAL_RTI_SMOKE=1

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
  export HLA2010_CERTI_PATCHED_PREFIX="${HLA2010_CERTI_PATCHED_PREFIX:-${HLA2010_CERTI_PREFIX:-$(default_state_path "CERTI-install")}}"
  export HLA2010_CERTI_PATCHED_BUILD_ROOT="${HLA2010_CERTI_PATCHED_BUILD_ROOT:-${HLA2010_CERTI_BUILD_ROOT:-$(default_state_path "CERTI-build")}}"
  export HLA2010_CERTI_PREFIX="$HLA2010_CERTI_PATCHED_PREFIX"
  export HLA2010_CERTI_BUILD_ROOT="$HLA2010_CERTI_PATCHED_BUILD_ROOT"
  require_runtime_prefix "patched CERTI install prefix" "${HLA2010_CERTI_PATCHED_PREFIX:-}"
  python -m pytest -q tests/vendors/test_real_vendor_runtime_smoke.py -k 'certi'
  python -m pytest -q \
    tests/vendors/test_certi_real_backend_exchange_matrix.py \
    tests/vendors/test_certi_real_backend_time_matrix.py \
    tests/vendors/test_certi_real_backend_ownership_matrix.py \
    -k 'not test_certi_upstream_time_query_and_fqr_baseline and not test_certi_patched_negotiated_ownership_baseline'
}

run_certi_upstream() {
  export HLA2010_CERTI_UPSTREAM_PREFIX="${HLA2010_CERTI_UPSTREAM_PREFIX:-$(default_state_path "CERTI-upstream-install")}"
  export HLA2010_CERTI_UPSTREAM_BUILD_ROOT="${HLA2010_CERTI_UPSTREAM_BUILD_ROOT:-$(default_state_path "CERTI-upstream-build")}"
  require_runtime_prefix "upstream CERTI install prefix" "${HLA2010_CERTI_UPSTREAM_PREFIX:-}"
  python -m pytest -q \
    tests/vendors/test_certi_real_backend_time_matrix.py \
    tests/vendors/test_certi_real_backend_ownership_matrix.py \
    -k 'test_certi_upstream_time_query_and_fqr_baseline or test_certi_upstream_queued_fqr_baseline or test_certi_upstream_negotiated_ownership_baseline or test_certi_upstream_release_request_branch_baseline'
}

run_certi_compare() {
  export HLA2010_CERTI_UPSTREAM_PREFIX="${HLA2010_CERTI_UPSTREAM_PREFIX:-$(default_state_path "CERTI-upstream-install")}"
  export HLA2010_CERTI_UPSTREAM_BUILD_ROOT="${HLA2010_CERTI_UPSTREAM_BUILD_ROOT:-$(default_state_path "CERTI-upstream-build")}"
  export HLA2010_CERTI_PATCHED_PREFIX="${HLA2010_CERTI_PATCHED_PREFIX:-${HLA2010_CERTI_PREFIX:-$(default_state_path "CERTI-install")}}"
  export HLA2010_CERTI_PATCHED_BUILD_ROOT="${HLA2010_CERTI_PATCHED_BUILD_ROOT:-${HLA2010_CERTI_BUILD_ROOT:-$(default_state_path "CERTI-build")}}"
  require_runtime_prefix "upstream CERTI install prefix" "${HLA2010_CERTI_UPSTREAM_PREFIX:-}"
  require_runtime_prefix "patched CERTI install prefix" "${HLA2010_CERTI_PATCHED_PREFIX:-}"
  python -m pytest -q \
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
  pitch)
    export HLA2010_PITCH_HOME="${HLA2010_PITCH_HOME:-$(default_pitch_home)}"
    test -n "${HLA2010_PITCH_HOME:-}" || { echo "Pitch runtime bundle is required"; exit 1; }
    export HLA2010_PITCH_USER_HOME="${HLA2010_PITCH_USER_HOME:-$("$ROOT_DIR/scripts/setup_pitch_state.sh")}"
    export HLA2010_PITCH_CRC_MODE="${HLA2010_PITCH_CRC_MODE:-docker}"
    export HLA2010_PITCH_DOCKER_BUILD="${HLA2010_PITCH_DOCKER_BUILD:-0}"
    python -m pytest -q tests/vendors/test_real_vendor_runtime_smoke.py -k 'pitch'
    python -m pytest -q tests/vendors/test_pitch_real_backend_matrix.py
    ;;
  matrix)
    "$0" certi
    "$0" pitch
    ;;
  all)
    python -m pytest -q tests/vendors/test_real_vendor_runtime_smoke.py
    ;;
  *)
    echo "usage: $0 [certi|certi-patched|certi-upstream|certi-compare|pitch|matrix|all]" >&2
    exit 2
    ;;
esac
