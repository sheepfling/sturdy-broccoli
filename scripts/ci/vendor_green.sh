#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
PROFILE="${1:-matrix}"
DELEGATE="${HLA2010_VENDOR_GREEN_DELEGATE:-$ROOT_DIR/scripts/ci/vendor_runtime_smoke.sh}"
CI_STATE_OUTPUT_DIR="${HLA2010_VENDOR_RUNTIME_CI_STATE_DIR:-$ROOT_DIR/artifacts/vendor_runtime_ci_state}"
CI_STATE_REQUIRED="${HLA2010_VENDOR_GREEN_REQUIRE_CI_STATE:-auto}"

# shellcheck source=../lib/shell.sh
source "$ROOT_DIR/scripts/lib/shell.sh"
hla2010_shell_init "$0"

ci_state_profile() {
  case "$1" in
    certi|certi-patched|certi-upstream|certi-compare|certi-save-restore|certi-save-restore-probe|certi-ddm|certi-ddm-probe)
      printf '%s\n' certi
      ;;
    pitch|pitch-smoke|pitch-verify|pitch-save-restore|pitch-save-restore-probe|pitch-ddm|pitch-ddm-probe|pitch-negotiated|pitch-negotiated-probe|pitch-time-window-probe|pitch-time-window-restore-state-probe|pitch-lost-federate|pitch-lost-federate-probe)
      printf '%s\n' pitch
      ;;
    matrix)
      printf '%s\n' matrix
      ;;
    vendor-edge)
      printf '%s\n' vendor-edge
      ;;
    all|"")
      printf '%s\n' all
      ;;
    *)
      printf '%s\n' all
      ;;
  esac
}

should_validate_ci_state() {
  case "$CI_STATE_REQUIRED" in
    1|true|yes|always)
      return 0
      ;;
    0|false|no|never)
      return 1
      ;;
    auto)
      [[ "${GITHUB_ACTIONS:-}" == "true" ]]
      ;;
    *)
      hla2010_shell_die "unsupported HLA2010_VENDOR_GREEN_REQUIRE_CI_STATE value: $CI_STATE_REQUIRED"
      ;;
  esac
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" || "${1:-}" == "help" ]]; then
  cat <<'EOF'
usage: ./scripts/ci/vendor_green.sh [profile]

Run the strict vendor-green lane.

- delegates to ./scripts/ci/vendor_runtime_smoke.sh
- forces HLA2010_VENDOR_PREFLIGHT_STRICT=1
- validates dedicated runner runtime-state before execution when running under CI
- fails immediately when CERTI or Pitch prerequisites are blocked
- always emits normalized vendor runtime status and parity artifacts on exit

Pitch profiles:
- pitch-smoke
- pitch-verify
- pitch-save-restore
- pitch-save-restore-probe
- pitch-ddm
- pitch-ddm-probe
- pitch-negotiated
- pitch-negotiated-probe
- pitch-time-window-probe
- pitch-time-window-restore-state-probe
- pitch-lost-federate
- pitch-lost-federate-probe
- pitch

CERTI profiles:
- certi-save-restore
- certi-save-restore-probe
- certi-ddm
- certi-ddm-probe

Use ./scripts/ci/repo_green.sh for the repo-green lane.
EOF
  exit 0
fi

export HLA2010_VENDOR_PREFLIGHT_STRICT=1
status=0
if should_validate_ci_state; then
  ci_profile="$(ci_state_profile "$PROFILE")"
  if "$(hla2010_shell_python_bin)" "$ROOT_DIR/scripts/ci/check_vendor_runtime_ci_state.py" \
    --profile "$ci_profile" \
    --output-dir "$CI_STATE_OUTPUT_DIR"; then
    :
  else
    status=$?
    "$ROOT_DIR/scripts/ci/emit_vendor_runtime_reports.sh" vendor-green "$PROFILE" || true
    exit "$status"
  fi
fi

if "$DELEGATE" "$PROFILE"; then
  status=0
else
  status=$?
fi

"$ROOT_DIR/scripts/ci/emit_vendor_runtime_reports.sh" vendor-green "$PROFILE" || true
exit "$status"
