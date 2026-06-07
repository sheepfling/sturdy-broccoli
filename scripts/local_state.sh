#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HLA2010_LOCAL_STATE_ROOT="${HLA2010_LOCAL_STATE_ROOT:-/private/tmp/hla-2010}"

local_state_path() {
  printf '%s/%s' "$HLA2010_LOCAL_STATE_ROOT" "$1"
}

ensure_local_state_dir_link() {
  local name="$1"
  local repo_path="$ROOT_DIR/$name"
  local state_path
  state_path="$(local_state_path "$name")"

  mkdir -p "$(dirname "$state_path")"

  if [[ -L "$repo_path" ]]; then
    local current_target
    current_target="$(readlink "$repo_path")"
    if [[ "$current_target" != "$state_path" ]]; then
      rm "$repo_path"
      ln -s "$state_path" "$repo_path"
    fi
  elif [[ -e "$repo_path" ]]; then
    if [[ -e "$state_path" ]]; then
      echo "error: both $repo_path and $state_path already exist; reconcile them manually" >&2
      exit 1
    fi
    mv "$repo_path" "$state_path"
    ln -s "$state_path" "$repo_path"
  else
    mkdir -p "$state_path"
    ln -s "$state_path" "$repo_path"
  fi

  mkdir -p "$state_path"
}

ensure_local_state_layout() {
  local paths=(
    ".venv"
    ".pytest_cache"
    ".mypy_cache"
    ".ruff_cache"
    "build"
    "downloads"
    "analysis"
    "verification"
    "htmlcov"
    "dist"
    "CERTI-build"
    "CERTI-install"
    "CERTI-upstream-source"
    "CERTI-upstream-build"
    "CERTI-upstream-install"
    "pitch-user-home"
  )

  local path
  for path in "${paths[@]}"; do
    ensure_local_state_dir_link "$path"
  done
}
