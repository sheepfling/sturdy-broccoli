#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# shellcheck disable=SC1091
source "$ROOT_DIR/scripts/local_state.sh"

usage() {
  cat <<'EOF'
usage: ./scripts/run_certi_local.sh <rtig|rtia> [args...]

Launch the local CERTI runtime binaries from the configured installation
prefix.
EOF
}

case "${1:-}" in
  help|-h|--help)
    usage
    exit 0
    ;;
esac

if [[ $# -lt 1 ]]; then
  usage
  exit 2
fi

backend="$1"
shift

case "$backend" in
  rtig|rtia)
    ;;
  *)
    echo "error: expected backend to be rtig or rtia"
    exit 2
    ;;
esac

certi_prefix="${HLA2010_CERTI_PREFIX:-}"
if [[ -z "$certi_prefix" ]]; then
  default_prefix="$(local_state_path "CERTI-install")"
  if [[ -d "$default_prefix" ]]; then
    certi_prefix="$default_prefix"
  fi
fi
if [[ -z "$certi_prefix" ]]; then
  echo "error: CERTI install prefix not found; set HLA2010_CERTI_PREFIX"
  exit 1
fi

certi_lib="$certi_prefix/lib"
certi_bin="$certi_prefix/bin"

exec env DYLD_LIBRARY_PATH="$certi_lib${DYLD_LIBRARY_PATH:+:$DYLD_LIBRARY_PATH}" \
  "$certi_bin/$backend" "$@"
