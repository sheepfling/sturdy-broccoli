#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  cat <<'EOF'
requirements_lint.sh: run the canonical imported HLA requirements packet gate.
Evidence:
- tests/verification/test_imported_hla_packet_v1_0.py
- tests/verification/test_imported_hla_packet_layout.py

This gate validates the committed v1.0 packet import:
- manifest-integrity rules for committed assets
- explicit omission policy for restricted IEEE source inputs
- canonical summary row counts
- required columns for the master catalog, verification matrix, and clause tracker
- master-catalog uniqueness and known source-gap expectations
- verification-matrix foreign-key integrity and P0/P1 coverage
- clause-tracker major-area coverage
- repo-native canonical packet-facing layout under requirements/latest, catalogs, history, dashboards, and manifests
EOF
  exit 0
fi

# shellcheck disable=SC1091
source "$ROOT_DIR/.venv/bin/activate"

python3 -m pytest \
  tests/verification/test_imported_hla_packet_v1_0.py \
  tests/verification/test_imported_hla_packet_layout.py \
  "$@"
