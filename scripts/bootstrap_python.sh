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
  "packages/hla2010-fom-minimal-demo"
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
  test   lean core workspace packages plus pytest and matplotlib
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

build_helper_deps=("setuptools>=68" "wheel" "packaging>=24")
helper_deps=()
if [[ "$want_pytest" == "1" ]]; then
  helper_deps+=("pytest" "py" "matplotlib" "fonttools" "kiwisolver" "grpcio" "protobuf")
fi
if [[ "$want_qa" == "1" ]]; then
  helper_deps+=("ruff" "pyright" "typing_extensions")
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
ROOT_REALPATH="$("$PYTHON_BIN" -c 'import os, sys; print(os.path.realpath(sys.argv[1]))' "$ROOT_DIR")"
ROOT_ALIAS_KEY="$("$PYTHON_BIN" -c 'import hashlib, sys; print(hashlib.sha256(sys.argv[1].encode("utf-8")).hexdigest()[:12])' "$ROOT_REALPATH")"
ROOT_ALIAS_DIR="/private/tmp/hla2010-workspace-$(id -un)-${ROOT_ALIAS_KEY}"
ROOT_ALIAS_PATH="$ROOT_ALIAS_DIR/repo"
VENV_ALIAS_DIR="$ROOT_ALIAS_PATH/.venv"

ensure_root_alias() {
  mkdir -p "$ROOT_ALIAS_DIR"
  if [[ -L "$ROOT_ALIAS_PATH" ]]; then
    local current_target
    current_target="$(readlink "$ROOT_ALIAS_PATH")"
    if [[ "$current_target" == "$ROOT_DIR" ]]; then
      return
    fi
    rm -f "$ROOT_ALIAS_PATH"
  elif [[ -e "$ROOT_ALIAS_PATH" ]]; then
    rm -rf "$ROOT_ALIAS_PATH"
  fi
  ln -s "$ROOT_DIR" "$ROOT_ALIAS_PATH"
}

venv_prefix_matches_root() {
  if [[ ! -x "$VENV_DIR/bin/python" ]]; then
    return 1
  fi
  local actual_prefix=""
  actual_prefix="$("$VENV_DIR/bin/python" -c 'import os, sys; print(os.path.realpath(sys.prefix))' 2>/dev/null || true)"
  [[ "$actual_prefix" == "$ROOT_REALPATH/.venv" ]]
}

ensure_root_alias
if [[ -x "$VENV_DIR/bin/python" ]]; then
  if venv_prefix_matches_root; then
    hla2010_shell_log "reusing existing venv at $VENV_DIR"
  else
    hla2010_shell_log "removing cross-bound venv at $VENV_DIR"
    "$PYTHON_BIN" -c 'from pathlib import Path; import shutil, sys; shutil.rmtree(Path(sys.argv[1]), ignore_errors=True)' "$VENV_DIR"
    hla2010_shell_log "creating venv via alias path $VENV_ALIAS_DIR"
    "$PYTHON_BIN" -m venv "$VENV_ALIAS_DIR"
  fi
else
  if [[ -d "$VENV_DIR" ]]; then
    hla2010_shell_log "removing broken venv at $VENV_DIR"
    "$PYTHON_BIN" -c 'from pathlib import Path; import shutil, sys; shutil.rmtree(Path(sys.argv[1]), ignore_errors=True)' "$VENV_DIR"
  fi
  hla2010_shell_log "creating venv via alias path $VENV_ALIAS_DIR"
  "$PYTHON_BIN" -m venv "$VENV_ALIAS_DIR"
fi

# Create the venv through an alias path with no spaces, then switch back to the
# canonical repo-local path so downstream tooling sees the expected workspace
# location.
export VIRTUAL_ENV="$VENV_DIR"
export PATH="$VENV_DIR/bin:$PATH"
VENV_PYTHON="$VENV_DIR/bin/python"

run_venv_python() {
  local python_bin="$VENV_DIR/bin/python"
  local status=0
  local attempt
  for attempt in 1 2 3; do
    if [[ ! -x "$python_bin" ]]; then
      sleep 1
      continue
    fi
    if "$python_bin" "$@"; then
      return 0
    fi
    status=$?
    if [[ "$status" -ne 127 ]]; then
      return "$status"
    fi
    hash -r
    sleep 1
  done
  return "$status"
}

site_packages_dir="$(run_venv_python -c 'import site; print(next(path for path in site.getsitepackages() if path.endswith("site-packages")))' )"

hla2010_shell_log "removing stale editable dist-info entries"
run_venv_python -c 'from pathlib import Path; import shutil, sys; site_packages = Path(sys.argv[1]); removed = []; 
for dist_info in sorted(site_packages.glob("*.dist-info")):
    metadata = dist_info / "METADATA"
    if metadata.exists():
        continue
    shutil.rmtree(dist_info, ignore_errors=True); removed.append(dist_info.name)
for stale_path in sorted(site_packages.glob("__editable__.* *.pth")):
    stale_path.unlink(missing_ok=True); removed.append(stale_path.name)
for stale_path in sorted(site_packages.glob("__editable___*_finder *.py")):
    stale_path.unlink(missing_ok=True); removed.append(stale_path.name)
print("\n".join(removed))' "$site_packages_dir"

hla2010_shell_log "installing helper dependencies profile=${hyperspec}"
run_venv_python -m ensurepip --upgrade
run_venv_python -m pip install --no-build-isolation "${build_helper_deps[@]}"
if [[ "${#helper_deps[@]}" -gt 0 ]]; then
  # Force a real reinstall so stale metadata-only helper packages cannot mask
  # missing runtime modules in reused venvs.
  run_venv_python -m pip install --no-build-isolation --upgrade --force-reinstall "${helper_deps[@]}"
fi
hyperspec_count="${#workspace_packages[@]}"
hla2010_shell_log "installing editable split packages count=${hyperspec_count}"
for package_dir in "${workspace_packages[@]}"; do
  hla2010_shell_log "installing editable package ${package_dir}"
  run_venv_python -c 'from pathlib import Path; import shutil, sys, tomllib; pyproject_path = Path(sys.argv[1]); site_packages = Path(sys.argv[2]); project = tomllib.loads(pyproject_path.read_text(encoding="utf-8")); project_name = project["project"]["name"]; normalized = project_name.replace("-", "_"); finder_prefix = normalized.replace(".", "_");
for path in sorted(site_packages.glob(f"{normalized}-*.dist-info")):
    shutil.rmtree(path, ignore_errors=True)
for path in sorted(site_packages.glob(f"__editable__.{normalized}-*.pth")):
    path.unlink(missing_ok=True)
for path in sorted(site_packages.glob(f"__editable___{finder_prefix}_*_finder.py")):
    path.unlink(missing_ok=True)' "$ROOT_DIR/$package_dir/pyproject.toml" "$site_packages_dir"
  run_venv_python -m pip install --no-build-isolation --no-deps -e "$ROOT_DIR/$package_dir"
done

run_venv_python -c 'import sys, tomllib; from pathlib import Path; root = Path(sys.argv[1]); site_packages_dir = Path(sys.argv[2]); workspace_pth = site_packages_dir / "hla2010_workspace_roots.pth"; pyproject = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8")); pythonpath_entries = [str(root / rel) for rel in pyproject["tool"]["pytest"]["ini_options"]["pythonpath"]]; workspace_pth.write_text("\n".join(pythonpath_entries) + "\n", encoding="utf-8"); print(workspace_pth)' "$ROOT_DIR" "$site_packages_dir"
hla2010_shell_log "wrote workspace roots file $site_packages_dir/hla2010_workspace_roots.pth"
