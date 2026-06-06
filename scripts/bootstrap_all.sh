#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

"$ROOT_DIR/scripts/bootstrap_python.sh"
"$ROOT_DIR/scripts/rebuild_certi.sh"
