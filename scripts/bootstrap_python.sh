#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON_BIN="${HLA2010_PYTHON:-python3}"
BOOTSTRAP_EXTRAS="${HLA2010_BOOTSTRAP_EXTRAS:-qa}"

# shellcheck source=lib/shell.sh
source "$ROOT_DIR/scripts/lib/shell.sh"
hla2010_shell_init "$0"

usage() {
  cat <<'EOF'
usage: ./scripts/bootstrap_python.sh

Create or refresh the local Python virtual environment and install the package
in editable mode with the configured extras.
EOF
}

case "${1:-}" in
  help|-h|--help)
    usage
    exit 0
    ;;
esac

hla2010_shell_log "bootstrap python extras=${BOOTSTRAP_EXTRAS}"
if ! hla2010_shell_have "$PYTHON_BIN"; then
  hla2010_shell_warn "requested python binary '$PYTHON_BIN' not found; falling back"
  PYTHON_BIN="$(hla2010_shell_python_bin)"
fi

# shellcheck disable=SC1091
source "$ROOT_DIR/scripts/local_state.sh"

ensure_local_state_layout
VENV_DIR="$(local_state_path ".venv")"

if [[ ! -d "$VENV_DIR" ]]; then
  hla2010_shell_log "creating venv at $VENV_DIR"
  "$PYTHON_BIN" -m venv --system-site-packages "$VENV_DIR"
else
  hla2010_shell_log "upgrading venv at $VENV_DIR"
  "$PYTHON_BIN" -m venv --system-site-packages --upgrade "$VENV_DIR"
fi

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"
hla2010_shell_log "installing editable package with extras [${BOOTSTRAP_EXTRAS}]"
python -m ensurepip --upgrade
python -m pip install --no-build-isolation -e ".[${BOOTSTRAP_EXTRAS}]"
