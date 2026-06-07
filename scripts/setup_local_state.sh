#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# shellcheck disable=SC1091
source "$ROOT_DIR/scripts/local_state.sh"

usage() {
  cat <<'EOF'
usage: ./scripts/setup_local_state.sh

Create the repo-managed temporary state layout used by local scripts.
EOF
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  case "${1:-}" in
    help|-h|--help)
      usage
      exit 0
      ;;
  esac
fi

ensure_local_state_layout
