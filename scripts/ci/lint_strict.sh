#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"

# shellcheck disable=SC1091
source "$ROOT_DIR/.venv/bin/activate"

ruff check src packages tests scripts tools \
  --select E9,F63,F7,F82,E501
