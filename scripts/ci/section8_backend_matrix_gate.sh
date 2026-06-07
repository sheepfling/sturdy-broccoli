#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"

if [[ -f "$ROOT_DIR/.venv/bin/activate" ]]; then
  # shellcheck disable=SC1091
  source "$ROOT_DIR/.venv/bin/activate"
fi

cd "$ROOT_DIR"

python3 -m pytest -q tests/time/test_section8_backend_matrix.py "$@"
python3 scripts/generate_compliance_artifacts.py

printf '%s\n' "updated analysis/compliance/section8_backend_matrix.json"
printf '%s\n' "updated analysis/compliance/section8_backend_matrix.md"
