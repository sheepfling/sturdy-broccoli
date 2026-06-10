#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
PROFILE="${1:-all}"

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  cat <<'EOF'
vendor_edge_matrix.sh: run the highest-value vendor edge slice.

Profiles:
- time-query: CERTI time-query/FQR compare plus the Pitch time-profile smoke
- negotiated-ownership: CERTI ownership compare plus the Pitch negotiated-ownership smoke
- all: run both profiles in sequence and refresh the compliance packet

Usage:
  ./scripts/ci/vendor_edge_matrix.sh [time-query|negotiated-ownership|all]
EOF
  exit 0
fi

if [[ -f "$ROOT_DIR/.venv/bin/activate" ]]; then
  # shellcheck disable=SC1091
  source "$ROOT_DIR/.venv/bin/activate"
fi

cd "$ROOT_DIR"

run_time_query() {
  ./scripts/ci/vendor_green.sh certi-compare
}

run_negotiated_ownership() {
  ./scripts/ci/vendor_green.sh pitch
}

case "$PROFILE" in
  time-query)
    run_time_query
    ;;
  negotiated-ownership)
    run_negotiated_ownership
    ;;
  all)
    run_time_query
    run_negotiated_ownership
    ;;
  *)
    echo "usage: $0 [time-query|negotiated-ownership|all]" >&2
    exit 2
    ;;
esac

python3 scripts/generate_compliance_artifacts.py

printf '%s\n' "updated analysis/compliance/*.json"
printf '%s\n' "updated analysis/compliance/*.md"
