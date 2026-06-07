#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"

if [[ -f "$ROOT_DIR/.venv/bin/activate" ]]; then
  # shellcheck disable=SC1091
  source "$ROOT_DIR/.venv/bin/activate"
fi

cd "$ROOT_DIR"

case "${1:-}" in
  help|-h|--help)
    python3 scripts/run_target_radar_proof.py --help
    exit 0
    ;;
esac

echo "running target/radar proof packet"

python3 scripts/run_target_radar_proof.py "$@"
