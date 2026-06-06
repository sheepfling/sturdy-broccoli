#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON_BIN="${HLA2010_PYTHON:-python3}"
BOOTSTRAP_EXTRAS="${HLA2010_BOOTSTRAP_EXTRAS:-qa}"

# shellcheck disable=SC1091
source "$ROOT_DIR/scripts/local_state.sh"

ensure_local_state_layout
VENV_DIR="$(local_state_path ".venv")"

if [[ ! -d "$VENV_DIR" ]]; then
  "$PYTHON_BIN" -m venv --system-site-packages "$VENV_DIR"
else
  "$PYTHON_BIN" -m venv --system-site-packages --upgrade "$VENV_DIR"
fi

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"
python -m ensurepip --upgrade
python -m pip install --no-build-isolation -e ".[${BOOTSTRAP_EXTRAS}]"
