#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
CERTI_SOURCE="${HLA2010_CERTI_SOURCE:-$ROOT_DIR/CERTI}"
CERTI_BUILD="${HLA2010_CERTI_BUILD:-$ROOT_DIR/CERTI-build}"
CERTI_INSTALL="${HLA2010_CERTI_PREFIX:-$ROOT_DIR/CERTI-install}"
CERTI_CMAKE_ARGS="${HLA2010_CERTI_CMAKE_ARGS:-}"
CERTI_BUILD_TARGETS="${HLA2010_CERTI_BUILD_TARGETS:-RTI1516e rtig rtia}"

if [[ ! -d "$CERTI_SOURCE" ]]; then
  echo "error: CERTI source not found at $CERTI_SOURCE"
  exit 1
fi

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
