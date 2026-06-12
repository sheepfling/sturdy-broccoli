#!/usr/bin/env bash

hla2010_shell_name() {
  local script_path="${1:-${BASH_SOURCE[1]}}"
  basename "$script_path"
}

hla2010_shell_log() {
  printf '[%s] %s\n' "${HLA2010_SCRIPT_NAME:-script}" "$*"
}

hla2010_shell_warn() {
  printf '[%s] warning: %s\n' "${HLA2010_SCRIPT_NAME:-script}" "$*" >&2
}

hla2010_shell_die() {
  printf '[%s] error: %s\n' "${HLA2010_SCRIPT_NAME:-script}" "$*" >&2
  exit 1
}

hla2010_shell_have() {
  command -v "$1" >/dev/null 2>&1
}

hla2010_shell_python_bin() {
  if [[ -n "${ROOT_DIR:-}" && -x "$ROOT_DIR/.venv/bin/python" ]]; then
    printf '%s\n' "$ROOT_DIR/.venv/bin/python"
    return 0
  fi
  if hla2010_shell_have python3; then
    command -v python3
    return 0
  fi
  if hla2010_shell_have python; then
    command -v python
    return 0
  fi
  hla2010_shell_die "python3 or python not found"
}

hla2010_shell_workspace_pythonpath() {
  [[ -n "${ROOT_DIR:-}" ]] || hla2010_shell_die "ROOT_DIR is required to build the workspace pythonpath"
  local python_bin
  python_bin="$(hla2010_shell_python_bin)"
  "$python_bin" - "$ROOT_DIR" <<'PY'
import os
import sys
import tomllib
from pathlib import Path

root = Path(sys.argv[1])
pyproject = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
source_roots = pyproject["tool"]["pytest"]["ini_options"]["pythonpath"]
print(os.pathsep.join(str(root / rel) for rel in source_roots))
PY
}

hla2010_shell_run_workspace_python() {
  local python_bin="$1"
  shift
  local workspace_pythonpath
  workspace_pythonpath="$(hla2010_shell_workspace_pythonpath)"
  PYTHONPATH="${workspace_pythonpath}${PYTHONPATH:+:$PYTHONPATH}" "$python_bin" "$@"
}

hla2010_shell_docker_host_gateway_arg() {
  case "$(uname -s)" in
    Linux)
      printf '%s\n' "--add-host=host.docker.internal:host-gateway"
      ;;
  esac
}

hla2010_shell_os_details() {
  case "$(uname -s)" in
    Darwin)
      if hla2010_shell_have sw_vers; then
        sw_vers 2>/dev/null | sed 's/^/    /'
      else
        uname -a
      fi
      ;;
    Linux)
      if [[ -r /etc/os-release ]]; then
        sed -n 's/^\(NAME\|VERSION\|PRETTY_NAME\)=/    \1=/p' /etc/os-release
      fi
      uname -a
      ;;
    *)
      uname -a
      ;;
  esac
}

hla2010_shell_on_error() {
  local status="$1"
  local command="$2"
  local line="$3"
  {
    printf '[%s] error: command failed with exit status %s\n' "${HLA2010_SCRIPT_NAME:-script}" "$status"
    printf '[%s] error: line %s: %s\n' "${HLA2010_SCRIPT_NAME:-script}" "$line" "$command"
    printf '[%s] cwd: %s\n' "${HLA2010_SCRIPT_NAME:-script}" "$PWD"
    printf '[%s] shell: bash %s on %s\n' "${HLA2010_SCRIPT_NAME:-script}" "${BASH_VERSION:-unknown}" "$(uname -s -r -m)"
    printf '[%s] os details:\n' "${HLA2010_SCRIPT_NAME:-script}"
    hla2010_shell_os_details | while IFS= read -r line; do
      printf '[%s] %s\n' "${HLA2010_SCRIPT_NAME:-script}" "$line"
    done
    if [[ -n "${ROOT_DIR:-}" ]]; then
      printf '[%s] root: %s\n' "${HLA2010_SCRIPT_NAME:-script}" "$ROOT_DIR"
      if [[ -d "$ROOT_DIR/.git" ]]; then
        local head
        head="$(git -C "$ROOT_DIR" rev-parse --short HEAD 2>/dev/null || true)"
        if [[ -n "$head" ]]; then
          printf '[%s] git: %s\n' "${HLA2010_SCRIPT_NAME:-script}" "$head"
        fi
      fi
    fi
    local i
    for ((i = 0; i < ${#FUNCNAME[@]} - 1; i++)); do
      printf '[%s] stack[%d]: %s at %s:%s\n' \
        "${HLA2010_SCRIPT_NAME:-script}" \
        "$i" \
        "${FUNCNAME[$i + 1]:-main}" \
        "${BASH_SOURCE[$i + 1]:-?}" \
        "${BASH_LINENO[$i]:-?}"
    done
  } >&2
}

hla2010_shell_init() {
  HLA2010_SCRIPT_NAME="${HLA2010_SCRIPT_NAME:-${1:-$(hla2010_shell_name)}}"
  export HLA2010_SCRIPT_NAME

  set -E
  if shopt -q inherit_errexit 2>/dev/null; then
    shopt -s inherit_errexit
  fi

  if [[ "${HLA2010_SHELL_DEBUG:-0}" != "0" ]]; then
    hla2010_shell_log "debug tracing enabled"
    export PS4='+${BASH_SOURCE##*/}:${LINENO}:${FUNCNAME[0]:-main}: '
    set -x
  fi

  trap 'hla2010_shell_on_error "$?" "$BASH_COMMAND" "$LINENO"' ERR
}
