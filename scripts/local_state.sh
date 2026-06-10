#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HLA2010_LOCAL_STATE_ROOT="${HLA2010_LOCAL_STATE_ROOT:-$ROOT_DIR/.local}"

normalize_local_state_key() {
  case "$1" in
    CERTI-build)
      printf '%s\n' "certi/patched/build"
      ;;
    CERTI-install)
      printf '%s\n' "certi/patched/install"
      ;;
    CERTI-upstream-source)
      printf '%s\n' "certi/upstream/source"
      ;;
    CERTI-upstream-build)
      printf '%s\n' "certi/upstream/build"
      ;;
    CERTI-upstream-install)
      printf '%s\n' "certi/upstream/install"
      ;;
    pitch-user-home)
      printf '%s\n' "pitch/user-home"
      ;;
    *)
      printf '%s\n' "$1"
      ;;
  esac
}

local_state_path() {
  printf '%s/%s' "$HLA2010_LOCAL_STATE_ROOT" "$(normalize_local_state_key "$1")"
}

ensure_local_state_layout() {
  local paths=(
    "CERTI-build"
    "CERTI-install"
    "CERTI-upstream-source"
    "CERTI-upstream-build"
    "CERTI-upstream-install"
    "pitch-user-home"
  )

  local path
  for path in "${paths[@]}"; do
    mkdir -p "$(local_state_path "$path")"
  done
}
