#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"

source "$ROOT_DIR/.venv/bin/activate"

ruff check hla2010 tests scripts tools --statistics
