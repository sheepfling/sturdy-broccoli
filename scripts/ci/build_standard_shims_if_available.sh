#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"

# shellcheck source=lib/shell.sh
source "$ROOT_DIR/scripts/lib/shell.sh"
hla2010_shell_init "$0"

if [[ "${HLA2010_SKIP_STANDARD_SHIM_BUILD:-0}" == "1" ]]; then
  hla2010_shell_log "standard shim artifact build skipped by HLA2010_SKIP_STANDARD_SHIM_BUILD=1"
  exit 0
fi

tool_works() {
  local tool="$1"
  local version_arg="$2"
  command -v "$tool" >/dev/null 2>&1 && "$tool" "$version_arg" >/dev/null 2>&1
}

build_target() {
  local target="$1"
  hla2010_shell_log "building $target"
  "$ROOT_DIR/tools/shim-routes" build "$target"
}

if tool_works javac -version && tool_works jar --version; then
  build_target java-standard-2010
  build_target java-standard-2025
else
  hla2010_shell_log "skipping Java standard shim builds; usable javac/jar not found"
fi

if tool_works c++ --version && command -v ar >/dev/null 2>&1; then
  build_target cpp-standard-2010
  build_target cpp-standard-2025
else
  hla2010_shell_log "skipping C++ standard shim builds; usable c++/ar not found"
fi
