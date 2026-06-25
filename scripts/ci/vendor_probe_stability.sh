#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
exec "${PYTHON:-python3}" "$ROOT_DIR/scripts/ci/run_vendor_probe_stability.py" "$@"
