#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
PROFILE="${1:-}"
REPEAT_COUNT="${2:-3}"
VENDOR_GREEN_CMD="${HLA2010_VENDOR_PROBE_STABILITY_VENDOR_GREEN:-$ROOT_DIR/scripts/ci/vendor_green.sh}"
OUTPUT_BASE_DIR="${HLA2010_VENDOR_PROBE_STABILITY_DIR:-$ROOT_DIR/analysis/vendor_probe_stability}"
CI_STATE_OUTPUT_DIR="${HLA2010_VENDOR_RUNTIME_CI_STATE_DIR:-$ROOT_DIR/analysis/vendor_runtime_ci_state}"
CI_STATE_REQUIRED="${HLA2010_VENDOR_PROBE_REQUIRE_CI_STATE:-auto}"
CI_STATE_CMD="${HLA2010_VENDOR_PROBE_CI_STATE_CMD:-}"

# shellcheck source=../lib/shell.sh
source "$ROOT_DIR/scripts/lib/shell.sh"
hla2010_shell_init "$0"

ci_state_profile() {
  case "$1" in
    certi|certi-patched|certi-upstream|certi-compare|certi-save-restore|certi-save-restore-probe|certi-ddm|certi-ddm-probe)
      printf '%s\n' certi
      ;;
    pitch|pitch-smoke|pitch-verify|pitch-save-restore|pitch-save-restore-probe|pitch-ddm|pitch-ddm-probe|pitch-negotiated|pitch-negotiated-probe|pitch-time-window-probe|pitch-lost-federate|pitch-lost-federate-probe)
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
      hla2010_shell_die "unsupported HLA2010_VENDOR_PROBE_REQUIRE_CI_STATE value: $CI_STATE_REQUIRED"
      ;;
  esac
}

run_ci_state_check() {
  local profile="$1"
  if [[ -n "$CI_STATE_CMD" ]]; then
    "$CI_STATE_CMD" --profile "$profile" --output-dir "$CI_STATE_OUTPUT_DIR"
    return
  fi
  "$(hla2010_shell_python_bin)" "$ROOT_DIR/scripts/ci/check_vendor_runtime_ci_state.py" \
    --profile "$profile" \
    --output-dir "$CI_STATE_OUTPUT_DIR"
}

render_operator_command() {
  case "$1" in
    certi-compare) echo "./tools/certi-easy smoke compare" ;;
    certi-save-restore) echo "./tools/certi-easy save-restore" ;;
    certi-save-restore-probe) echo "./tools/certi-easy save-restore-probe" ;;
    certi-ddm) echo "./tools/certi-easy ddm" ;;
    certi-ddm-probe) echo "./tools/certi-easy ddm-probe" ;;
    pitch|pitch-smoke) echo "./tools/pitch smoke" ;;
    pitch-save-restore) echo "./tools/pitch save-restore" ;;
    pitch-save-restore-probe) echo "./tools/pitch save-restore-probe" ;;
    pitch-ddm) echo "./tools/pitch ddm" ;;
    pitch-ddm-probe) echo "./tools/pitch ddm-probe" ;;
    pitch-negotiated) echo "./tools/pitch negotiated" ;;
    pitch-negotiated-probe) echo "./tools/pitch negotiated-probe" ;;
    pitch-time-window-probe) echo "./tools/pitch time-window-probe" ;;
    pitch-lost-federate) echo "./tools/pitch lost-federate" ;;
    pitch-lost-federate-probe) echo "./tools/pitch lost-federate-probe" ;;
    *) echo "$VENDOR_GREEN_CMD $1" ;;
  esac
}

if [[ -z "${PROFILE}" || "${PROFILE}" == "-h" || "${PROFILE}" == "--help" ]]; then
  cat <<'EOF'
vendor_probe_stability.sh: run a vendor profile repeatedly and emit stability artifacts.

Usage:
  ./scripts/ci/vendor_probe_stability.sh <profile> [repeat-count]

Examples:
  ./scripts/ci/vendor_probe_stability.sh pitch-negotiated-probe 5
  ./scripts/ci/vendor_probe_stability.sh certi-ddm-probe 3

Artifacts:
  analysis/vendor_probe_stability/<profile>/vendor_probe_stability_summary.json
  analysis/vendor_probe_stability/<profile>/vendor_probe_stability_report.md
EOF
  exit 0
fi

if [[ -f "$ROOT_DIR/.venv/bin/activate" ]]; then
  # shellcheck disable=SC1091
  source "$ROOT_DIR/.venv/bin/activate"
fi

if should_validate_ci_state; then
  ci_profile="$(ci_state_profile "$PROFILE")"
  run_ci_state_check "$ci_profile"
fi

mkdir -p "$OUTPUT_BASE_DIR/$PROFILE"
attempts_file="$OUTPUT_BASE_DIR/$PROFILE/attempts.csv"
printf 'iteration,exit_code,duration_seconds\n' >"$attempts_file"

overall_status=0
iteration=1
while [[ "$iteration" -le "$REPEAT_COUNT" ]]; do
  SECONDS=0
  if HLA2010_VENDOR_GREEN_REQUIRE_CI_STATE=0 "$VENDOR_GREEN_CMD" "$PROFILE"; then
    status=0
  else
    status=$?
    overall_status=1
  fi
  duration="$SECONDS"
  printf '%s,%s,%s\n' "$iteration" "$status" "$duration" >>"$attempts_file"
  iteration=$((iteration + 1))
done

"$(hla2010_shell_python_bin)" "$ROOT_DIR/scripts/ci/write_vendor_probe_stability.py" \
  --profile "$PROFILE" \
  --repeat-count "$REPEAT_COUNT" \
  --command "$(render_operator_command "$PROFILE")" \
  --executor-command "$VENDOR_GREEN_CMD $PROFILE" \
  --attempts-file "$attempts_file" \
  --output-dir "$OUTPUT_BASE_DIR/$PROFILE" >/dev/null

exit "$overall_status"
