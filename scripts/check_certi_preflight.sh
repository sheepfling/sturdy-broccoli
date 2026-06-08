#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
OUTPUT_JSON=0

for arg in "$@"; do
  case "$arg" in
    --json)
      OUTPUT_JSON=1
      ;;
  esac
done

# shellcheck source=lib/shell.sh
source "$ROOT_DIR/scripts/lib/shell.sh"
hla2010_shell_init "$0"

VENV_PYTHON="$ROOT_DIR/.venv/bin/python"

if [[ "$OUTPUT_JSON" -eq 1 ]]; then
  python_bin="$(hla2010_shell_python_bin)"
  exec "$python_bin" "$ROOT_DIR/scripts/check_certi_preflight.py" "$@"
fi

show_hint() {
  local title="$1"
  local detail="$2"
  printf '[%s] %s: %s\n' "${HLA2010_SCRIPT_NAME:-script}" "$title" "$detail"
}

show_hint "CERTI preflight" "starting"
show_hint "platform" "$(uname -s -r -m)"

if [[ ! -x "$VENV_PYTHON" ]]; then
  show_hint "python env" "blocked: missing .venv"
  show_hint "next step" "./bootstrap certi or ./certi-easy install"
  show_hint "result" "not ready; bootstrap Python first"
  exit 1
fi

show_hint "python env" "ok: $VENV_PYTHON"

if "$VENV_PYTHON" "$ROOT_DIR/scripts/check_certi_preflight.py" "$@"; then
  exit 0
fi

exit 1
