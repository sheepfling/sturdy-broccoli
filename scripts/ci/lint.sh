#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  cat <<'EOF'
lint.sh: run the required lint/syntax gate.
Evidence:
- ruff E9/F63/F7/F82 on src, package-owned source roots, tests, scripts, tools
- python compileall on repo Python sources
- canonical imported requirements packet validation
- generated-doc sync check
EOF
  exit 0
fi

# shellcheck disable=SC1091
source "$ROOT_DIR/.venv/bin/activate"

RUFF_TARGETS=(
  "src"
  "packages"
  "tests"
  "scripts"
  "tools"
)

ruff check "${RUFF_TARGETS[@]}" --select E9,F63,F7,F82

COMPILE_TARGETS=()
for target in src packages tests scripts tools; do
    if [ -d "$ROOT_DIR/$target" ] && find "$ROOT_DIR/$target" -name '*.py' -print -quit | grep -q .; then
        COMPILE_TARGETS+=("$target")
    fi
done

python -m compileall -q "${COMPILE_TARGETS[@]}"
"$ROOT_DIR/scripts/ci/requirements_lint.sh"
"$ROOT_DIR/scripts/ci/check_generated_docs.sh"
