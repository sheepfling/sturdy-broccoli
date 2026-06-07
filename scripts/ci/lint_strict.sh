#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"

# shellcheck disable=SC1091
source "$ROOT_DIR/.venv/bin/activate"

ruff check hla2010 tests scripts tools \
  --select E9,F63,F7,F82,E501 \
  --extend-per-file-ignores \
  "hla2010/backends/python_rti.py:E501,hla2010/exceptions.py:E501,hla2010/raw_api.py:E501"
