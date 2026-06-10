#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
PROFILE="${1:-matrix}"
DELEGATE="${HLA2010_VENDOR_GREEN_DELEGATE:-$ROOT_DIR/scripts/ci/vendor_runtime_smoke.sh}"

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" || "${1:-}" == "help" ]]; then
  cat <<'EOF'
usage: ./scripts/ci/vendor_green.sh [profile]

Run the strict vendor-green lane.

- delegates to ./scripts/ci/vendor_runtime_smoke.sh
- forces HLA2010_VENDOR_PREFLIGHT_STRICT=1
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
if "$DELEGATE" "$PROFILE"; then
  status=0
else
  status=$?
fi

"$ROOT_DIR/scripts/ci/emit_vendor_runtime_reports.sh" vendor-green "$PROFILE" || true
exit "$status"
