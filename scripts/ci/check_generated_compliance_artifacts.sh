#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
COMPLIANCE_DIR="$ROOT_DIR/analysis/compliance"
TMP_ROOT="$(mktemp -d)"
SNAPSHOT_DIR="$TMP_ROOT/compliance.before"

# shellcheck source=../lib/shell.sh
source "$ROOT_DIR/scripts/lib/shell.sh"
hla2010_shell_init "$0"
PYTHON_BIN="$(hla2010_shell_python_bin)"

cleanup() {
  if [[ -d "$SNAPSHOT_DIR" ]]; then
    rm -rf "$COMPLIANCE_DIR"
    mkdir -p "$(dirname "$COMPLIANCE_DIR")"
    cp -R "$SNAPSHOT_DIR" "$COMPLIANCE_DIR"
  fi
  rm -rf "$TMP_ROOT"
}

usage() {
  cat <<'EOF'
usage: ./scripts/ci/check_generated_compliance_artifacts.sh

Run the compliance artifact generator, fail if it would change the committed
analysis/compliance packet, and restore the pre-run workspace snapshot before
exiting.

Implementation note:
- the script copies `analysis/compliance/` into a temporary
  `compliance.before/` snapshot under a temp root
- that snapshot is comparison-only restore state for this check, not a live
  owner surface or manager-facing handoff packet
EOF
}

case "${1:-}" in
  help|-h|--help)
    usage
    exit 0
    ;;
esac

trap cleanup EXIT

mkdir -p "$SNAPSHOT_DIR"
if [[ -d "$COMPLIANCE_DIR" ]]; then
  cp -R "$COMPLIANCE_DIR/." "$SNAPSHOT_DIR/"
fi

cd "$ROOT_DIR"
hla2010_shell_log "regenerating compliance artifacts"
hla2010_shell_run_workspace_python "$PYTHON_BIN" scripts/generate_compliance_artifacts.py

if ! diff -qr "$SNAPSHOT_DIR" "$COMPLIANCE_DIR" >/dev/null; then
  printf '%s\n' "error: generated compliance artifacts are stale." >&2
  printf '%s\n' "run: python3 scripts/generate_compliance_artifacts.py" >&2
  diff -qr "$SNAPSHOT_DIR" "$COMPLIANCE_DIR" || true
  exit 1
fi

hla2010_shell_log "compliance artifacts are current"
