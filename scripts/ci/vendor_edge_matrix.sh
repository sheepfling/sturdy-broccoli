#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
PROFILE="${1:-all}"
VENDOR_GREEN_CMD="${HLA2010_VENDOR_EDGE_VENDOR_GREEN:-$ROOT_DIR/scripts/ci/vendor_green.sh}"
COMPLIANCE_GENERATOR="${HLA2010_VENDOR_EDGE_COMPLIANCE_GENERATOR:-python3 scripts/generate_compliance_artifacts.py}"

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  cat <<'EOF'
vendor_edge_matrix.sh: run the highest-value vendor edge slice.

Profiles:
- time-query: CERTI time-query/FQR compare plus the Pitch time-profile smoke
- negotiated-ownership: CERTI ownership compare plus the Pitch negotiated-ownership smoke
- save-restore: CERTI and Pitch save/restore probe slices
- ddm: CERTI and Pitch DDM probe slices
- all: run both profiles in sequence and refresh the compliance packet

Usage:
  ./scripts/ci/vendor_edge_matrix.sh [time-query|negotiated-ownership|save-restore|ddm|all]
EOF
  exit 0
fi

if [[ -f "$ROOT_DIR/.venv/bin/activate" ]]; then
  # shellcheck disable=SC1091
  source "$ROOT_DIR/.venv/bin/activate"
fi

cd "$ROOT_DIR"

run_time_query() {
  "$VENDOR_GREEN_CMD" certi-compare
  "$VENDOR_GREEN_CMD" pitch-smoke
}

run_negotiated_ownership() {
  "$VENDOR_GREEN_CMD" certi-compare
  "$VENDOR_GREEN_CMD" pitch-negotiated-probe
}

run_save_restore() {
  "$VENDOR_GREEN_CMD" certi-save-restore-probe
  "$VENDOR_GREEN_CMD" pitch-save-restore-probe
}

run_ddm() {
  "$VENDOR_GREEN_CMD" certi-ddm-probe
  "$VENDOR_GREEN_CMD" pitch-ddm-probe
}

case "$PROFILE" in
  time-query)
    run_time_query
    ;;
  negotiated-ownership)
    run_negotiated_ownership
    ;;
  save-restore)
    run_save_restore
    ;;
  ddm)
    run_ddm
    ;;
  all)
    run_time_query
    run_negotiated_ownership
    run_save_restore
    run_ddm
    ;;
  *)
    echo "usage: $0 [time-query|negotiated-ownership|save-restore|ddm|all]" >&2
    exit 2
    ;;
esac

eval "$COMPLIANCE_GENERATOR"

printf '%s\n' "updated analysis/compliance/*.json"
printf '%s\n' "updated analysis/compliance/*.md"
