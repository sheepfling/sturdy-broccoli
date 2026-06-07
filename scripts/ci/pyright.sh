#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  cat <<'EOF'
pyright.sh: run the scoped static typing gate.
Evidence:
- python -m pyright -p pyrightconfig.json
EOF
  exit 0
fi

# shellcheck disable=SC1091
source "$ROOT_DIR/.venv/bin/activate"

python3 -m pyright -p "$ROOT_DIR/pyrightconfig.json"
