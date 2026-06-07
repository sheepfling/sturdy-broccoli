#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"

# shellcheck disable=SC1091
source "$ROOT_DIR/.venv/bin/activate"

python3 -m pyright -p "$ROOT_DIR/pyrightconfig.json"
