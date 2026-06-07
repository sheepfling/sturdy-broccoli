#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"

run_stage() {
  local stage="$1"
  shift
  local attempt=1
  local max_attempts=2
  while :; do
    if "$@"; then
      return 0
    fi
    status=$?
    if [[ $status -ne 137 || $attempt -ge $max_attempts ]]; then
      return "$status"
    fi
    echo "retrying $stage after SIGKILL" >&2
    attempt=$((attempt + 1))
  done
}

run_stage lint "$ROOT_DIR/scripts/ci/lint.sh"
run_stage test "$ROOT_DIR/scripts/ci/test.sh" "$@"
