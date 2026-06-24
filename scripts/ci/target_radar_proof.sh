#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"

# shellcheck source=lib/shell.sh
source "$ROOT_DIR/scripts/lib/shell.sh"
hla2010_shell_init "$0"
PYTHON_BIN="$(hla2010_shell_python_bin)"

if [[ -f "$ROOT_DIR/.venv/bin/activate" ]]; then
  # shellcheck disable=SC1091
  source "$ROOT_DIR/.venv/bin/activate"
fi

cd "$ROOT_DIR"

case "${1:-}" in
  help|-h|--help)
    "$PYTHON_BIN" scripts/run_target_radar_proof.py --help
    exit 0
    ;;
esac

hla2010_shell_log "running target/radar proof packet"
hla2010_shell_log "python: $PYTHON_BIN"

if [[ "$#" -eq 0 ]]; then
  "$PYTHON_BIN" scripts/run_target_radar_proof.py --backend python1516e --proof-backend python1516e
else
  "$PYTHON_BIN" scripts/run_target_radar_proof.py "$@"
fi
