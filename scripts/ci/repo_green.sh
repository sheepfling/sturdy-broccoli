#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
DELEGATE="${HLA2010_REPO_GREEN_DELEGATE:-$ROOT_DIR/scripts/ci/full_sequence.sh}"

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" || "${1:-}" == "help" ]]; then
  cat <<'EOF'
usage: ./scripts/ci/repo_green.sh

Run the repo-green verification lane.

- delegates to ./scripts/ci/full_sequence.sh
- keeps vendor runtime checks repo-green friendly
- blocked CERTI/Pitch prerequisites skip cleanly after mandatory preflight
- always emits normalized vendor runtime status and parity artifacts on exit

Use ./scripts/ci/vendor_green.sh for the strict real-runtime lane.
EOF
  exit 0
fi

status=0
if "$DELEGATE" "$@"; then
  status=0
else
  status=$?
fi

"$ROOT_DIR/scripts/ci/emit_vendor_runtime_reports.sh" repo-green all || true
exit "$status"
