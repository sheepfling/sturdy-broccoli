#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VENV_PYTHON="$ROOT_DIR/.venv/bin/python"

if [[ -x "$VENV_PYTHON" ]]; then
  exec "$VENV_PYTHON" "$ROOT_DIR/scripts/check_pitch_preflight.py" "$@"
fi
if command -v python3 >/dev/null 2>&1; then
  exec python3 "$ROOT_DIR/scripts/check_pitch_preflight.py" "$@"
fi
exec python "$ROOT_DIR/scripts/check_pitch_preflight.py" "$@"
