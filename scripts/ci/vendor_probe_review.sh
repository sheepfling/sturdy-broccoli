#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
PROFILE="${1:-}"
REPEAT_COUNT="${2:-5}"
STABILITY_CMD="${HLA2010_VENDOR_PROBE_REVIEW_STABILITY_CMD:-$ROOT_DIR/scripts/ci/vendor_probe_stability.sh}"
PROMOTION_REVIEW_CMD="${HLA2010_VENDOR_PROBE_REVIEW_PROMOTION_CMD:-python3 $ROOT_DIR/scripts/ci/write_vendor_probe_promotion_review.py}"
PARITY_CMD="${HLA2010_VENDOR_PROBE_REVIEW_PARITY_CMD:-python3 $ROOT_DIR/scripts/run_vendor_parity_artifacts.py}"

if [[ -z "$PROFILE" || "$PROFILE" == "-h" || "$PROFILE" == "--help" ]]; then
  cat <<'EOF'
vendor_probe_review.sh: run repeated probe stability, promotion review, and parity refresh.

Usage:
  ./scripts/ci/vendor_probe_review.sh <profile> [repeat-count]

Examples:
  ./scripts/ci/vendor_probe_review.sh pitch-negotiated-probe 5
  ./scripts/ci/vendor_probe_review.sh certi-ddm-probe 5
EOF
  exit 0
fi

if [[ -f "$ROOT_DIR/.venv/bin/activate" ]]; then
  # shellcheck disable=SC1091
  source "$ROOT_DIR/.venv/bin/activate"
fi

"$STABILITY_CMD" "$PROFILE" "$REPEAT_COUNT"
eval "$PROMOTION_REVIEW_CMD"
eval "$PARITY_CMD"
