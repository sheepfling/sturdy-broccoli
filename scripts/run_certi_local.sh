#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

if [[ $# -lt 1 ]]; then
  echo "usage: $0 <rtig|rtia> [args...]"
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
if [[ -z "$certi_prefix" && -d "$ROOT_DIR/third_party/certi/install" ]]; then
  certi_prefix="$ROOT_DIR/third_party/certi/install"
fi
if [[ -z "$certi_prefix" && -d "$ROOT_DIR/../hla-python/INBOX/CERTI-install" ]]; then
  certi_prefix="$ROOT_DIR/../hla-python/INBOX/CERTI-install"
fi
if [[ -z "$certi_prefix" ]]; then
  echo "error: CERTI install prefix not found; set HLA2010_CERTI_PREFIX"
  exit 1
fi

certi_lib="$certi_prefix/lib"
certi_bin="$certi_prefix/bin"

exec env DYLD_LIBRARY_PATH="$certi_lib${DYLD_LIBRARY_PATH:+:$DYLD_LIBRARY_PATH}" \
  "$certi_bin/$backend" "$@"
