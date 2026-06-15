#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" || "${1:-}" == "help" ]]; then
  cat <<'EOF'
usage: ./scripts/ci/python_fast.sh

Run the fast Python/operator verification lane.

- activates the repo virtualenv
- runs a curated low-cost slice of operator, docs, and Python matrix checks
- avoids real vendor runtime dependencies
EOF
  exit 0
fi

# shellcheck disable=SC1091
source "$ROOT_DIR/.venv/bin/activate"

python -m pytest -q \
  tests/test_operator_setup_policy.py \
  tests/test_operator_doc_surfaces.py \
  tests/test_operator_tools_inventory.py \
  tests/test_documentation_navigation_policy.py \
  tests/test_documentation_namespace_policy.py \
  tests/test_python_matrix_policy.py \
  "$@"
