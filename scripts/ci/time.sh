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
  "packages/hla2010-rti-python/src"
  "packages/hla2010-rti-certi/src"
  "packages/hla2010-rti-backend-common/src"
  "packages/hla2010-rti-java-common/src"
  "packages/hla2010-rti-runtime-common/src"
  "packages/hla2010-rti-java-jpype/src"
  "packages/hla2010-rti-java-py4j/src"
  "packages/hla2010-rti-pitch-common/src"
  "packages/hla2010-rti-pitch-jpype/src"
  "packages/hla2010-rti-pitch-py4j/src"
  "packages/hla2010-rti-portico/src"
  "packages/hla2010-fom-target-radar/src"
  "packages/hla2010-verification-harness/src"
)

SOURCE_PATH="$(IFS=:; printf '%s' "${SOURCE_ROOTS[*]}")"
export PYTHONPATH="$SOURCE_PATH${PYTHONPATH:+:$PYTHONPATH}"

"$PYTHON_BIN" -m pytest tests/time -q "$@"
