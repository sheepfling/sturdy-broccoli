#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
CERTI_SOURCE="${HLA2010_CERTI_SOURCE:-$ROOT_DIR/CERTI}"
CERTI_CMAKE_ARGS="${HLA2010_CERTI_CMAKE_ARGS:-}"
CERTI_BUILD_TARGETS="${HLA2010_CERTI_BUILD_TARGETS:-RTI1516e rtig rtia}"

# shellcheck source=lib/shell.sh
source "$ROOT_DIR/scripts/lib/shell.sh"
hla2010_shell_init "$0"

# shellcheck disable=SC1091
source "$ROOT_DIR/scripts/local_state.sh"

ensure_local_state_layout

CERTI_BUILD="${HLA2010_CERTI_BUILD:-$(local_state_path "CERTI-build")}"
CERTI_INSTALL="${HLA2010_CERTI_PREFIX:-$(local_state_path "CERTI-install")}"

if [[ ! -d "$CERTI_SOURCE" ]]; then
  hla2010_shell_die "CERTI source not found at $CERTI_SOURCE"
fi

hla2010_shell_log "CERTI source: $CERTI_SOURCE"
hla2010_shell_log "CERTI build: $CERTI_BUILD"
hla2010_shell_log "CERTI install: $CERTI_INSTALL"

cmake_args=(
  --fresh
  -S "$CERTI_SOURCE"
  -B "$CERTI_BUILD"
  -DCMAKE_INSTALL_PREFIX="$CERTI_INSTALL"
  -DCMAKE_POLICY_VERSION_MINIMUM=3.5
  -DCERTI_BUILD_LEGACY_TEST_UTILITIES=OFF
)
if [[ -n "$CERTI_CMAKE_ARGS" ]]; then
  # shellcheck disable=SC2206
  extra_cmake_args=($CERTI_CMAKE_ARGS)
  cmake_args+=("${extra_cmake_args[@]}")
fi

cmake "${cmake_args[@]}"

if [[ -n "$CERTI_BUILD_TARGETS" ]]; then
  # shellcheck disable=SC2206
  build_targets=($CERTI_BUILD_TARGETS)
else
  build_targets=(RTI1516e rtig rtia)
fi

cmake --build "$CERTI_BUILD" --target "${build_targets[@]}"
cmake --install "$CERTI_BUILD"
