#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"

# shellcheck disable=SC1091
source "$ROOT_DIR/.venv/bin/activate"

if [[ "$#" -eq 0 ]]; then
  python -m pytest -q
else
  python -m pytest -q "$@"
fi
