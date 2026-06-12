#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
DOC_PATH="$ROOT_DIR/docs/rti_options_and_test_matrix.md"
GENERATOR="$ROOT_DIR/scripts/update_rti_options_matrix.py"
TMP_DOC="$(mktemp)"

# shellcheck source=../lib/shell.sh
source "$ROOT_DIR/scripts/lib/shell.sh"
hla2010_shell_init "$0"
PYTHON_BIN="$(hla2010_shell_python_bin)"

cleanup() {
  if [[ -f "$TMP_DOC" ]]; then
    cp "$TMP_DOC" "$DOC_PATH"
    rm -f "$TMP_DOC"
  fi
}

trap cleanup EXIT

cp "$DOC_PATH" "$TMP_DOC"
(
  cd "$ROOT_DIR"
  "$PYTHON_BIN" "$GENERATOR"
)

if ! cmp -s "$DOC_PATH" "$TMP_DOC"; then
  printf '%s\n' "error: generated backend alias inventory is stale." >&2
  printf '%s\n' "run: python3 scripts/update_rti_options_matrix.py" >&2
  exit 1
fi

(
  cd "$ROOT_DIR"
  "$PYTHON_BIN" "$ROOT_DIR/scripts/ci/check_doc_links.py"
)
