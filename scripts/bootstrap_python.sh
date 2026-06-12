#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON_BIN="${HLA2010_PYTHON:-python3}"
EXTRAS_RAW="${HLA2010_BOOTSTRAP_EXTRAS:-test}"
CORE_WORKSPACE_PACKAGES=(
  "packages/hla2010-spec"
  "packages/hla2010-rti-backend-common"
  "packages/hla2010-rti-runtime-common"
  "packages/hla2010-rti-transport-common"
  "packages/hla2010-rti-java-common"
  "packages/hla2010-rti-python"
  "packages/hla2010-rti-certi"
  "packages/hla2010-rti-pitch-common"
  "packages/hla2010-rti-transport-grpc"
  "packages/hla2010-rti-transport-rest"
  "packages/hla2010-verification-harness"
  "packages/hla2010-fom-target-radar"
)
JPYPE_WORKSPACE_PACKAGES=(
  "packages/hla2010-rti-java-jpype"
  "packages/hla2010-rti-pitch-jpype"
)
PY4J_WORKSPACE_PACKAGES=(
  "packages/hla2010-rti-java-py4j"
  "packages/hla2010-rti-pitch-py4j"
)
DUAL_BRIDGE_WORKSPACE_PACKAGES=(
  "packages/hla2010-rti-portico"
)

# shellcheck source=lib/shell.sh
source "$ROOT_DIR/scripts/lib/shell.sh"
hla2010_shell_init "$0"

usage() {
  cat <<'EOF'
usage: ./scripts/bootstrap_python.sh

Create or refresh the local Python virtual environment and install the split
workspace packages in editable mode.

Supported extras via HLA2010_BOOTSTRAP_EXTRAS:
  test   lean core workspace packages plus pytest
  jpype  core workspace plus the JPype bridge packages
  py4j   core workspace plus the Py4J bridge packages
  java   core workspace plus both bridge families and Portico
  qa     full repo-green workspace plus pytest, Ruff, and Pyright

Combine values with commas when needed, for example:
  HLA2010_BOOTSTRAP_EXTRAS=qa,java ./scripts/bootstrap_python.sh

Planning helpers:
  ./scripts/bootstrap_python.sh plan
  ./scripts/bootstrap_python.sh plan-json
EOF
}

case "${1:-}" in
  help|-h|--help)
    usage
    exit 0
    ;;
esac

want_pytest=1
want_qa=0
want_jpype=0
want_py4j=0

IFS=',' read -r -a extras_tokens <<< "$EXTRAS_RAW"
for raw_token in "${extras_tokens[@]}"; do
  token="${raw_token//[[:space:]]/}"
  case "$token" in
    ""|test)
      ;;
    qa)
      want_qa=1
      want_jpype=1
      want_py4j=1
      ;;
    jpype)
      want_jpype=1
      ;;
    py4j)
      want_py4j=1
      ;;
    java)
      want_jpype=1
      want_py4j=1
      ;;
    *)
      echo "error: unsupported HLA2010_BOOTSTRAP_EXTRAS token: $token" >&2
      echo "supported values: test, qa, jpype, py4j, java" >&2
      exit 2
      ;;
  esac
done

helper_deps=()
if [[ "$want_pytest" == "1" ]]; then
  helper_deps+=("pytest")
fi
if [[ "$want_qa" == "1" ]]; then
  helper_deps+=("ruff" "pyright")
fi
if [[ "$want_jpype" == "1" ]]; then
  helper_deps+=("jpype1")
fi
if [[ "$want_py4j" == "1" ]]; then
  helper_deps+=("py4j")
fi

workspace_packages=("${CORE_WORKSPACE_PACKAGES[@]}")
if [[ "$want_jpype" == "1" ]]; then
  workspace_packages+=("${JPYPE_WORKSPACE_PACKAGES[@]}")
fi
if [[ "$want_py4j" == "1" ]]; then
  workspace_packages+=("${PY4J_WORKSPACE_PACKAGES[@]}")
fi
if [[ "$want_jpype" == "1" && "$want_py4j" == "1" ]]; then
  workspace_packages+=("${DUAL_BRIDGE_WORKSPACE_PACKAGES[@]}")
fi

hyperspec="core"
if [[ "$want_jpype" == "1" && "$want_py4j" == "1" ]]; then
  hyperspec="full-java"
elif [[ "$want_jpype" == "1" ]]; then
  hyperspec="jpype"
elif [[ "$want_py4j" == "1" ]]; then
  hyperspec="py4j"
fi

case "${1:-}" in
  plan)
    printf 'extras=%s\n' "$EXTRAS_RAW"
    printf 'profile=%s\n' "$hyperspec"
    printf 'helper_deps=%s\n' "${helper_deps[*]}"
    printf 'workspace_packages=%s\n' "${workspace_packages[*]}"
    exit 0
    ;;
  plan-json)
    python3 - "$EXTRAS_RAW" "$hyperspec" "${helper_deps[*]}" "${workspace_packages[*]}" <<'PY'
import json
import sys

extras, profile, helper_deps, workspace_packages = sys.argv[1:]
print(json.dumps(
    {
        "extras": extras,
        "profile": profile,
        "helper_deps": [item for item in helper_deps.split() if item],
        "workspace_packages": [item for item in workspace_packages.split() if item],
    },
    indent=2,
    sort_keys=True,
))
PY
    exit 0
    ;;
esac

hla2010_shell_log "bootstrap python split-package workspace extras=${EXTRAS_RAW}"
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
hla2010_shell_log "installing helper dependencies profile=${hyperspec}"
python -m ensurepip --upgrade
python -m pip install --no-build-isolation "${helper_deps[@]}"
hyperspec_count="${#workspace_packages[@]}"
hla2010_shell_log "installing editable split packages count=${hyperspec_count}"
editable_args=()
for package_dir in "${workspace_packages[@]}"; do
  editable_args+=("-e" "$ROOT_DIR/$package_dir")
done
python -m pip install --no-build-isolation "${editable_args[@]}"
