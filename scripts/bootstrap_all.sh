#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# shellcheck source=lib/shell.sh
source "$ROOT_DIR/scripts/lib/shell.sh"
hla2010_shell_init "$0"

usage() {
  cat <<'EOF'
usage: ./scripts/bootstrap_all.sh

Bootstrap the Python environment, then rebuild CERTI.
This is the combined local setup path for the full repo toolchain.
EOF
}

case "${1:-}" in
  help|-h|--help)
    usage
    exit 0
    ;;
esac

hla2010_shell_log "bootstrap all -> python + certi"
"$ROOT_DIR/scripts/bootstrap_python.sh"
"$ROOT_DIR/scripts/rebuild_certi.sh"
