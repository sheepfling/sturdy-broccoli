#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
EXTRAS="${HLA2010_BOOTSTRAP_EXTRAS:-qa}"

"$ROOT_DIR/scripts/bootstrap_python.sh"

# shellcheck disable=SC1091
source "$ROOT_DIR/.venv/bin/activate"
python -m pip install --upgrade pip
python -m pip install --no-build-isolation -e ".[${EXTRAS}]"
