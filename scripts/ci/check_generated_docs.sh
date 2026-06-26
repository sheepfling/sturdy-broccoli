#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
DOC_PATHS=(
  "$ROOT_DIR/docs/rti_options_and_test_matrix.md"
  "$ROOT_DIR/docs/reference/java_interface_spec_mapping.md"
  "$ROOT_DIR/docs/fom-examples/fom_inventory.md"
  "$ROOT_DIR/docs/reference/hla_interface_contracts.md"
)
GENERATORS=(
  "$ROOT_DIR/scripts/update_rti_options_matrix.py"
  "$ROOT_DIR/scripts/generate_java_interface_spec_mapping.py"
  "$ROOT_DIR/scripts/generate_fom_inventory_view.py"
  "$ROOT_DIR/scripts/generate_hla_interface_contracts.py"
)
GENERATOR_ARGS=(
  ""
  ""
  ""
  "check-docs"
)
REGEN_HINTS=(
  "python3 scripts/update_rti_options_matrix.py"
  "python3 scripts/generate_java_interface_spec_mapping.py"
  "python3 scripts/generate_fom_inventory_view.py"
  "python3 scripts/generate_hla_interface_contracts.py generate-docs"
)
ERROR_MESSAGES=(
  "error: generated backend alias inventory is stale."
  "error: generated Java interface spec mapping is stale."
  "error: generated FOM inventory markdown view is stale."
  "error: generated HLA interface contracts doc is stale."
)
TMP_DOCS=()

# shellcheck source=../lib/shell.sh
source "$ROOT_DIR/scripts/lib/shell.sh"
hla2010_shell_init "$0"
PYTHON_BIN="$(hla2010_shell_python_bin)"

cleanup() {
  local index tmp_doc
  for index in "${!TMP_DOCS[@]}"; do
    tmp_doc="${TMP_DOCS[$index]}"
    if [[ -f "$tmp_doc" ]]; then
      cp "$tmp_doc" "${DOC_PATHS[$index]}"
      rm -f "$tmp_doc"
    fi
  done
}

trap cleanup EXIT

for doc_path in "${DOC_PATHS[@]}"; do
  tmp_doc="$(mktemp)"
  TMP_DOCS+=("$tmp_doc")
  cp "$doc_path" "$tmp_doc"
done

for index in "${!GENERATORS[@]}"; do
  (
    cd "$ROOT_DIR"
    if [[ -n "${GENERATOR_ARGS[$index]}" ]]; then
      "$PYTHON_BIN" "${GENERATORS[$index]}" "${GENERATOR_ARGS[$index]}"
    else
      "$PYTHON_BIN" "${GENERATORS[$index]}"
    fi
  )
done

for index in "${!DOC_PATHS[@]}"; do
  if ! cmp -s "${DOC_PATHS[$index]}" "${TMP_DOCS[$index]}"; then
    printf '%s\n' "${ERROR_MESSAGES[$index]}" >&2
    printf '%s\n' "run: ${REGEN_HINTS[$index]}" >&2
    exit 1
  fi
done

(
  cd "$ROOT_DIR"
  "$PYTHON_BIN" "$ROOT_DIR/scripts/ci/check_doc_links.py"
)
