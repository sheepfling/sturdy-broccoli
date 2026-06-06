#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# shellcheck disable=SC1091
source "$ROOT_DIR/scripts/local_state.sh"

ensure_local_state_layout

REMOTE_NAME="${1:-local}"
REPO_NAME="$(basename "$ROOT_DIR")"
REMOTE_ROOT="$(local_state_path "git-remotes")"
REMOTE_PATH="${2:-$REMOTE_ROOT/${REPO_NAME}.git}"

mkdir -p "$(dirname "$REMOTE_PATH")"

if [[ ! -d "$REMOTE_PATH" ]]; then
  git init --bare "$REMOTE_PATH"
fi

if git -C "$ROOT_DIR" remote get-url "$REMOTE_NAME" >/dev/null 2>&1; then
  git -C "$ROOT_DIR" remote set-url "$REMOTE_NAME" "$REMOTE_PATH"
else
  git -C "$ROOT_DIR" remote add "$REMOTE_NAME" "$REMOTE_PATH"
fi

printf '%s\n' "$REMOTE_PATH"
