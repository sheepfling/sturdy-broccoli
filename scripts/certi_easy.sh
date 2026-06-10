#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# shellcheck source=lib/shell.sh
source "$ROOT_DIR/scripts/lib/shell.sh"
hla2010_shell_init "$0"

# shellcheck disable=SC1091
source "$ROOT_DIR/scripts/local_state.sh"

ensure_local_state_layout

PATCHED_SOURCE="${HLA2010_CERTI_SOURCE:-$ROOT_DIR/CERTI}"
PATCHED_BUILD="${HLA2010_CERTI_BUILD:-$(local_state_path "CERTI-build")}"
PATCHED_PREFIX="${HLA2010_CERTI_PREFIX:-$(local_state_path "CERTI-install")}"
UPSTREAM_SOURCE="${HLA2010_CERTI_UPSTREAM_SOURCE:-$(local_state_path "CERTI-upstream-source")}"
UPSTREAM_BUILD="${HLA2010_CERTI_UPSTREAM_BUILD_ROOT:-$(local_state_path "CERTI-upstream-build")}"
UPSTREAM_PREFIX="${HLA2010_CERTI_UPSTREAM_PREFIX:-$(local_state_path "CERTI-upstream-install")}"
VENV_PYTHON="$ROOT_DIR/.venv/bin/python"
PREFLIGHT_ARTIFACT_DIR="${HLA2010_PREFLIGHT_ARTIFACT_DIR:-$ROOT_DIR/analysis/preflight_artifacts}"

usage() {
  cat <<'EOF'
Usage:
  ./scripts/certi_easy.sh install
  ./scripts/certi_easy.sh preflight [--json] [--json-file FILE]
  ./scripts/certi_easy.sh doctor
  ./scripts/certi_easy.sh paths
  ./scripts/certi_easy.sh build [patched|upstream|all]
  ./scripts/certi_easy.sh run [patched|upstream] [rtig|rtia] [args...]
  ./scripts/certi_easy.sh smoke [patched|upstream|compare]
  ./scripts/certi_easy.sh save-restore
  ./scripts/certi_easy.sh save-restore-probe
  ./scripts/certi_easy.sh save-restore-review [repeat-count]
  ./scripts/certi_easy.sh ddm
  ./scripts/certi_easy.sh ddm-probe
  ./scripts/certi_easy.sh ddm-review [repeat-count]
  ./scripts/certi_easy.sh test [patched|upstream|compare]

What these mean:
  install   bootstrap Python, build patched CERTI, clone/build pristine upstream CERTI
  doctor    show where everything lives and whether real CERTI smoke can run here
  build     rebuild one or both CERTI variants
  run       launch rtig or rtia for patched or upstream CERTI
  smoke     run the supported real-runtime smoke/matrix profile
  save-restore report the current real-runtime save/restore gap profile
  save-restore-probe run the current narrow real-runtime save/restore probe
  save-restore-review run repeated review for the save/restore probe and refresh promotion/parity artifacts
  ddm       report the current real-runtime DDM gap profile
  ddm-probe run the current narrow real-runtime DDM probe
  ddm-review run repeated review for the DDM probe and refresh promotion/parity artifacts
  test      alias for smoke

Simple path:
  ./scripts/certi_easy.sh install
  ./scripts/certi_easy.sh preflight [--json] [--json-file FILE]
  ./scripts/certi_easy.sh doctor
  ./scripts/certi_easy.sh smoke compare
EOF
}

die() {
  echo "error: $*" >&2
  exit 1
}

require_venv() {
  [[ -x "$VENV_PYTHON" ]] || die "missing .venv. Run ./scripts/certi_easy.sh install first."
}

preflight_certi() {
  "$ROOT_DIR/scripts/check_certi_preflight.sh" "$@"
}

certi_preflight_artifact_path() {
  printf '%s/%s\n' "$PREFLIGHT_ARTIFACT_DIR" "certi-preflight.json"
}

preflight_has_json_file() {
  local arg
  for arg in "$@"; do
    case "$arg" in
      --json-file|--json-file=*)
        return 0
        ;;
    esac
  done
  return 1
}

run_persisted_certi_preflight() {
  mkdir -p "$PREFLIGHT_ARTIFACT_DIR"
  local artifact_path
  artifact_path="$(certi_preflight_artifact_path)"
  if preflight_has_json_file "$@"; then
    preflight_certi "$@"
  else
    preflight_certi "$@" --json-file "$artifact_path"
  fi
}

emit_certi_runtime_reports() {
  local profile="${1:-certi}"
  "$ROOT_DIR/scripts/ci/emit_vendor_runtime_reports.sh" vendor-green "$profile" || true
}

variant_or_default() {
  local variant="${1:-all}"
  case "$variant" in
    patched|upstream|all|compare)
      printf '%s\n' "$variant"
      ;;
    *)
      die "unknown CERTI variant '$variant'"
      ;;
  esac
}

show_paths() {
  cat <<EOF
CERTI paths
  patched source : $PATCHED_SOURCE
  patched build  : $PATCHED_BUILD
  patched install: $PATCHED_PREFIX
  upstream source: $UPSTREAM_SOURCE
  upstream build : $UPSTREAM_BUILD
  upstream install: $UPSTREAM_PREFIX
  python venv    : $ROOT_DIR/.venv
EOF
}

show_preflight_summary() {
  local environment="$1"
  local result="$2"
  local next_step="$3"
  echo "environment: $environment"
  echo "result: $result"
  echo "next step: $next_step"
}

run_python_bootstrap() {
  hla2010_shell_log "bootstrapping python"
  "$ROOT_DIR/scripts/bootstrap_python.sh"
}

run_build() {
  local variant
  variant="$(variant_or_default "${1:-all}")"
  hla2010_shell_log "CERTI build variant=${variant}"
  case "$variant" in
    patched)
      "$ROOT_DIR/scripts/rebuild_certi.sh"
      ;;
    upstream)
      "$ROOT_DIR/scripts/rebuild_certi_upstream.sh"
      ;;
    all|compare)
      "$ROOT_DIR/scripts/rebuild_certi.sh"
      "$ROOT_DIR/scripts/rebuild_certi_upstream.sh"
      ;;
  esac
}

run_install() {
  run_python_bootstrap
  run_build all
}

show_doctor() {
  show_paths
  echo
  echo "Patched CERTI install:"
  if [[ -x "$PATCHED_PREFIX/bin/rtig" ]]; then
    echo "  ok: $PATCHED_PREFIX/bin/rtig"
  else
    echo "  missing: patched rtig not built yet"
  fi
  echo "Upstream CERTI install:"
  if [[ -x "$UPSTREAM_PREFIX/bin/rtig" ]]; then
    echo "  ok: $UPSTREAM_PREFIX/bin/rtig"
  else
    echo "  missing: upstream rtig not built yet"
  fi
  echo
  local summary_json
  local python_bin
  local preflight_status=0
  python_bin="$(hla2010_shell_python_bin)"
  summary_json="$("$python_bin" "$ROOT_DIR/scripts/check_certi_preflight.py" --json || true)"
  if preflight_certi >/dev/null; then
    preflight_status=0
  else
    preflight_status=$?
  fi
  if [[ -n "$summary_json" ]]; then
    "$python_bin" - "$summary_json" <<'PY'
import json
import sys

payload = json.loads(sys.argv[1])
environment = payload.get("environment", "unknown")
result = payload.get("result", "unknown")
next_steps = payload.get("next_steps") or []
if "will skip" in result and len(next_steps) > 1:
    next_step = next_steps[1]
elif next_steps:
    next_step = next_steps[0]
else:
    next_step = "./scripts/certi_easy.sh preflight"
print(f"environment: {environment}")
print(f"result: {result}")
print(f"next step: {next_step}")
PY
  fi
  return "$preflight_status"
}

run_variant_binary() {
  local variant="$1"
  local binary="$2"
  shift 2
  if preflight_certi; then
    :
  else
    return $?
  fi
  case "$variant" in
    patched)
      HLA2010_CERTI_PREFIX="$PATCHED_PREFIX" "$ROOT_DIR/scripts/run_certi_local.sh" "$binary" "$@"
      ;;
    upstream)
      HLA2010_CERTI_PREFIX="$UPSTREAM_PREFIX" "$ROOT_DIR/scripts/run_certi_local.sh" "$binary" "$@"
      ;;
    *)
      die "run requires patched or upstream"
      ;;
  esac
}

run_smoke() {
  local profile="${1:-compare}"
  local preflight_status=0
  require_venv
  if run_persisted_certi_preflight; then
    :
  else
    preflight_status=$?
    case "$profile" in
      patched)
        emit_certi_runtime_reports "certi-patched"
        ;;
      upstream)
        emit_certi_runtime_reports "certi-upstream"
        ;;
      compare)
        emit_certi_runtime_reports "certi-compare"
        ;;
      *)
        emit_certi_runtime_reports "certi"
        ;;
    esac
    return "$preflight_status"
  fi
  hla2010_shell_log "CERTI smoke profile=${profile}"
  case "$profile" in
    patched)
      "$ROOT_DIR/scripts/ci/vendor_green.sh" certi-patched
      ;;
    upstream)
      "$ROOT_DIR/scripts/ci/vendor_green.sh" certi-upstream
      ;;
    compare)
      "$ROOT_DIR/scripts/ci/vendor_green.sh" certi-compare
      ;;
    *)
      die "smoke requires patched, upstream, or compare"
      ;;
  esac
}

COMMAND="${1:-help}"
case "$COMMAND" in
  help|-h|--help)
    usage
    ;;
  preflight)
    preflight_status=0
    if run_persisted_certi_preflight "${@:2}"; then
      preflight_status=0
    else
      preflight_status=$?
    fi
    emit_certi_runtime_reports
    exit "$preflight_status"
    ;;
  install)
    run_install
    ;;
  doctor)
    doctor_status=0
    if show_doctor; then
      doctor_status=0
    else
      doctor_status=$?
    fi
    exit "$doctor_status"
    ;;
  paths)
    show_paths
    ;;
  build)
    run_build "${2:-all}"
    ;;
  run)
    [[ $# -ge 3 ]] || die "usage: ./scripts/certi_easy.sh run [patched|upstream] [rtig|rtia] [args...]"
    run_status=0
    if run_variant_binary "$2" "$3" "${@:4}"; then
      run_status=0
    else
      run_status=$?
    fi
    exit "$run_status"
    ;;
  smoke|test)
    smoke_status=0
    if run_smoke "${2:-compare}"; then
      smoke_status=0
    else
      smoke_status=$?
    fi
    exit "$smoke_status"
    ;;
  save-restore)
    save_restore_status=0
    if "$ROOT_DIR/scripts/ci/vendor_green.sh" certi-save-restore; then
      save_restore_status=0
    else
      save_restore_status=$?
    fi
    exit "$save_restore_status"
    ;;
  save-restore-probe)
    save_restore_probe_status=0
    if "$ROOT_DIR/scripts/ci/vendor_green.sh" certi-save-restore-probe; then
      save_restore_probe_status=0
    else
      save_restore_probe_status=$?
    fi
    exit "$save_restore_probe_status"
    ;;
  save-restore-review)
    save_restore_review_status=0
    if bash "$ROOT_DIR/scripts/ci/vendor_probe_review.sh" certi-save-restore-probe "${2:-5}"; then
      save_restore_review_status=0
    else
      save_restore_review_status=$?
    fi
    exit "$save_restore_review_status"
    ;;
  ddm)
    ddm_status=0
    if "$ROOT_DIR/scripts/ci/vendor_green.sh" certi-ddm; then
      ddm_status=0
    else
      ddm_status=$?
    fi
    exit "$ddm_status"
    ;;
  ddm-probe)
    ddm_probe_status=0
    if "$ROOT_DIR/scripts/ci/vendor_green.sh" certi-ddm-probe; then
      ddm_probe_status=0
    else
      ddm_probe_status=$?
    fi
    exit "$ddm_probe_status"
    ;;
  ddm-review)
    ddm_review_status=0
    if bash "$ROOT_DIR/scripts/ci/vendor_probe_review.sh" certi-ddm-probe "${2:-5}"; then
      ddm_review_status=0
    else
      ddm_review_status=$?
    fi
    exit "$ddm_review_status"
    ;;
  *)
    usage
    exit 2
    ;;
esac
