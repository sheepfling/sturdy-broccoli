#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  cat <<'EOF'
test.sh: run pytest for the full suite or the selected paths.
Evidence:
- python -m pytest -q
EOF
  exit 0
fi

# shellcheck disable=SC1091
source "$ROOT_DIR/.venv/bin/activate"

if [[ "$#" -eq 0 ]]; then
  python -m pytest -q
else
  python -m pytest -q "$@"
fi
