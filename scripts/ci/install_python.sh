#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
EXTRAS="${HLA2010_BOOTSTRAP_EXTRAS:-qa}"

# shellcheck source=lib/shell.sh
source "$ROOT_DIR/scripts/lib/shell.sh"
hla2010_shell_init "$0"

usage() {
  cat <<'EOF'
usage: ./scripts/ci/install_python.sh

Create or refresh the local Python environment, then install the package in
split-package workspace in editable mode for the quality gates.
EOF
}

case "${1:-}" in
  help|-h|--help)
    usage
    exit 0
    ;;
esac

hla2010_shell_log "install python extras=${EXTRAS}"
HLA2010_BOOTSTRAP_EXTRAS="$EXTRAS" "$ROOT_DIR/scripts/bootstrap_python.sh"
hla2010_shell_log "split workspace already installed by bootstrap; root stays tooling-only"
