#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
LANE="${1:-repo-green}"
PROFILE="${2:-all}"
PREFLIGHT_ARTIFACT_DIR="${HLA2010_PREFLIGHT_ARTIFACT_DIR:-$ROOT_DIR/analysis/preflight_artifacts}"
STATUS_BASE_DIR="${HLA2010_VENDOR_RUNTIME_STATUS_DIR:-$ROOT_DIR/analysis/vendor_runtime_status}"
PARITY_OUTPUT_DIR="${HLA2010_VENDOR_PARITY_ARTIFACT_DIR:-$ROOT_DIR/analysis/vendor_parity_artifacts}"

# shellcheck source=../lib/shell.sh
source "$ROOT_DIR/scripts/lib/shell.sh"
hla2010_shell_init "$0"

python_bin() {
  if [[ -x "$ROOT_DIR/.venv/bin/python" ]]; then
    printf '%s\n' "$ROOT_DIR/.venv/bin/python"
    return 0
  fi
  if command -v python3 >/dev/null 2>&1; then
    command -v python3
    return 0
  fi
  if command -v python >/dev/null 2>&1; then
    command -v python
    return 0
  fi
  return 1
}

vendors_for_profile() {
  case "$1" in
    certi|certi-patched|certi-upstream|certi-compare|certi-save-restore|certi-save-restore-probe|certi-ddm|certi-ddm-probe)
      printf '%s\n' certi
      ;;
    pitch|pitch-smoke|pitch-verify|pitch-save-restore|pitch-save-restore-probe|pitch-ddm|pitch-ddm-probe|pitch-negotiated|pitch-negotiated-probe)
      printf '%s\n' pitch
      ;;
    matrix|all|"")
      printf '%s\n' certi pitch
      ;;
    *)
      printf '%s\n' certi pitch
      ;;
  esac
}

status_output_dir() {
  if [[ "$LANE" == "repo-green" ]]; then
    printf '%s\n' "$STATUS_BASE_DIR/repo_green"
    return 0
  fi
  local normalized_profile="${PROFILE//-/_}"
  printf '%s\n' "$STATUS_BASE_DIR/vendor_green_${normalized_profile}"
}

main() {
  local py
  py="$(python_bin)" || {
    hla2010_shell_warn "skipping vendor runtime report emission because no Python interpreter is available"
    return 0
  }

  local output_dir
  output_dir="$(status_output_dir)"
  local -a vendor_args=()
  local vendor
  while IFS= read -r vendor; do
    [[ -n "$vendor" ]] || continue
    vendor_args+=(--vendor "$vendor")
  done < <(vendors_for_profile "$PROFILE")

  mkdir -p "$STATUS_BASE_DIR" "$PARITY_OUTPUT_DIR"

  if ! "$py" "$ROOT_DIR/scripts/classify_vendor_runtime.py" \
    --artifact-dir "$PREFLIGHT_ARTIFACT_DIR" \
    --output-dir "$output_dir" \
    --lane "$LANE" \
    "${vendor_args[@]}"; then
    hla2010_shell_warn "vendor runtime status classification reported a non-green state for lane $LANE"
  fi

  if ! "$py" "$ROOT_DIR/scripts/run_vendor_parity_artifacts.py" --output-dir "$PARITY_OUTPUT_DIR"; then
    hla2010_shell_warn "vendor parity artifact generation failed"
  fi
}

main "$@"
