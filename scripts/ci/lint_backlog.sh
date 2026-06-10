#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"

source "$ROOT_DIR/.venv/bin/activate"

ruff check src packages tests scripts tools --statistics
