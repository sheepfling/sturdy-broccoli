#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON_BIN="${HLA2010_PYTHON:-python3}"
WORKSPACE_PACKAGES=(
  "packages/hla2010-spec"
  "packages/hla2010-rti-backend-common"
  "packages/hla2010-rti-runtime-common"
  "packages/hla2010-rti-transport-common"
  "packages/hla2010-rti-java-common"
  "packages/hla2010-rti-python"
  "packages/hla2010-rti-certi"
  "packages/hla2010-rti-java-jpype"
  "packages/hla2010-rti-java-py4j"
  "packages/hla2010-rti-pitch-common"
  "packages/hla2010-rti-pitch-jpype"
  "packages/hla2010-rti-pitch-py4j"
  "packages/hla2010-rti-portico"
  "packages/hla2010-rti-transport-grpc"
  "packages/hla2010-rti-transport-rest"
  "packages/hla2010-verification-harness"
  "packages/hla2010-fom-target-radar"
)

# shellcheck source=lib/shell.sh
source "$ROOT_DIR/scripts/lib/shell.sh"
hla2010_shell_init "$0"

usage() {
  cat <<'EOF'
usage: ./scripts/bootstrap_python.sh

Create or refresh the local Python virtual environment and install the split
workspace packages in editable mode.
EOF
}

case "${1:-}" in
  help|-h|--help)
    usage
    exit 0
    ;;
esac

hla2010_shell_log "bootstrap python split-package workspace"
if ! hla2010_shell_have "$PYTHON_BIN"; then
  hla2010_shell_warn "requested python binary '$PYTHON_BIN' not found; falling back"
  PYTHON_BIN="$(hla2010_shell_python_bin)"
fi

VENV_DIR="$ROOT_DIR/.venv"

if [[ ! -d "$VENV_DIR" ]]; then
  hla2010_shell_log "creating venv at $VENV_DIR"
  "$PYTHON_BIN" -m venv --system-site-packages "$VENV_DIR"
else
  hla2010_shell_log "upgrading venv at $VENV_DIR"
  "$PYTHON_BIN" -m venv --system-site-packages --upgrade "$VENV_DIR"
fi

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"
hla2010_shell_log "installing editable split packages"
python -m ensurepip --upgrade
python -m pip install --no-build-isolation pytest ruff pyright
editable_args=()
for package_dir in "${WORKSPACE_PACKAGES[@]}"; do
  editable_args+=("-e" "$ROOT_DIR/$package_dir")
done
python -m pip install --no-build-isolation "${editable_args[@]}"
