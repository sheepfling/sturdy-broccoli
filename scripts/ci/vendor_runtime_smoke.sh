#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
PROFILE="${1:-all}"

# shellcheck disable=SC1091
source "$ROOT_DIR/.venv/bin/activate"

export HLA2010_ENABLE_REAL_RTI_SMOKE=1

case "$PROFILE" in
  certi)
    test -n "${HLA2010_CERTI_PREFIX:-}" || { echo "HLA2010_CERTI_PREFIX is required"; exit 1; }
    python -m pytest -q tests/test_real_vendor_runtime_smoke.py -k 'certi'
    python -m pytest -q tests/test_certi_real_backend_matrix.py
    ;;
  pitch)
    test -n "${HLA2010_PITCH_HOME:-}" || { echo "HLA2010_PITCH_HOME is required"; exit 1; }
    test -n "${HLA2010_PITCH_USER_HOME:-}" || { echo "HLA2010_PITCH_USER_HOME is required"; exit 1; }
    python -m pytest -q tests/test_real_vendor_runtime_smoke.py -k 'pitch'
    python -m pytest -q tests/test_pitch_real_backend_matrix.py
    ;;
  all)
    python -m pytest -q tests/test_real_vendor_runtime_smoke.py
    ;;
  *)
    echo "usage: $0 [certi|pitch|all]" >&2
    exit 2
    ;;
esac
