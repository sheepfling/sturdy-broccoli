#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
PYTHON_BIN="${PYTHON:-python}"

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  cat <<'EOF'
time.sh: run the pure-Python HLA 1516.1-2010 time-management suite.
Evidence:
- python -m pytest tests/time -q
EOF
  exit 0
fi

if [[ -f "$ROOT_DIR/.venv/bin/activate" ]]; then
  # shellcheck disable=SC1091
  source "$ROOT_DIR/.venv/bin/activate"
  PYTHON_BIN="${PYTHON:-python}"
fi

cd "$ROOT_DIR"

SOURCE_ROOTS=(
  "src"
  "packages/hla-backend-inmemory/src"
  "packages/hla-backend-certi/src"
  "packages/hla-backend-common/src"
  "packages/hla-bridge-java-common/src"
  "packages/hla-rti-core/src"
  "packages/hla-bridge-java-jpype/src"
  "packages/hla-bridge-java-py4j/src"
  "packages/hla-vendor-pitch/src"
  "packages/hla-vendor-pitch-jpype/src"
  "packages/hla-vendor-pitch-py4j/src"
  "packages/hla-vendor-portico/src"
  "packages/hla-fom-target-radar/src"
  "packages/hla-verification/src"
)

SOURCE_PATH="$(IFS=:; printf '%s' "${SOURCE_ROOTS[*]}")"
export PYTHONPATH="$SOURCE_PATH${PYTHONPATH:+:$PYTHONPATH}"

"$PYTHON_BIN" -m pytest tests/time -q "$@"
