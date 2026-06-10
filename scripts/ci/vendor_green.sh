#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
PROFILE="${1:-matrix}"

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" || "${1:-}" == "help" ]]; then
  cat <<'EOF'
usage: ./scripts/ci/vendor_green.sh [profile]

Run the strict vendor-green lane.

- delegates to ./scripts/ci/vendor_runtime_smoke.sh
- forces HLA2010_VENDOR_PREFLIGHT_STRICT=1
- fails immediately when CERTI or Pitch prerequisites are blocked

Use ./scripts/ci/repo_green.sh for the repo-green lane.
EOF
  exit 0
fi

export HLA2010_VENDOR_PREFLIGHT_STRICT=1
exec "$ROOT_DIR/scripts/ci/vendor_runtime_smoke.sh" "$PROFILE"
