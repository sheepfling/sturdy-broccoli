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
editable mode with the configured extras.
EOF
}

case "${1:-}" in
  help|-h|--help)
    usage
    exit 0
    ;;
esac

hla2010_shell_log "install python extras=${EXTRAS}"

"$ROOT_DIR/scripts/bootstrap_python.sh"

# shellcheck disable=SC1091
source "$ROOT_DIR/.venv/bin/activate"
hla2010_shell_log "pip install editable package with extras [${EXTRAS}]"
python -m pip install --upgrade pip
python -m pip install --no-build-isolation -e ".[${EXTRAS}]"
