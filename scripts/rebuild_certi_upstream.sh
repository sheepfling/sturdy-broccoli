#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# shellcheck source=lib/shell.sh
source "$ROOT_DIR/scripts/lib/shell.sh"
hla2010_shell_init "$0"

# shellcheck disable=SC1091
source "$ROOT_DIR/scripts/local_state.sh"

ensure_local_state_layout

CERTI_UPSTREAM_REPO="${HLA2010_CERTI_UPSTREAM_REPO:-https://github.com/etopzone/CERTI.git}"
CERTI_UPSTREAM_REF="${HLA2010_CERTI_UPSTREAM_REF:-master}"
CERTI_UPSTREAM_SOURCE="${HLA2010_CERTI_UPSTREAM_SOURCE:-$(local_state_path "CERTI-upstream-source")}"
CERTI_UPSTREAM_BUILD="${HLA2010_CERTI_UPSTREAM_BUILD_ROOT:-$(local_state_path "CERTI-upstream-build")}"
CERTI_UPSTREAM_INSTALL="${HLA2010_CERTI_UPSTREAM_PREFIX:-$(local_state_path "CERTI-upstream-install")}"

if [[ ! -d "$CERTI_UPSTREAM_SOURCE/.git" ]]; then
  if [[ -e "$CERTI_UPSTREAM_SOURCE" && -n "$(find "$CERTI_UPSTREAM_SOURCE" -mindepth 1 -maxdepth 1 -print -quit)" ]]; then
    hla2010_shell_die "$CERTI_UPSTREAM_SOURCE exists but is not an empty git checkout"
  fi
  git clone "$CERTI_UPSTREAM_REPO" "$CERTI_UPSTREAM_SOURCE"
fi

git -C "$CERTI_UPSTREAM_SOURCE" fetch --tags origin
git -C "$CERTI_UPSTREAM_SOURCE" checkout "$CERTI_UPSTREAM_REF"

build_log="$(mktemp -t hla2010-certi-upstream-build)"
hla2010_shell_log "CERTI upstream source: $CERTI_UPSTREAM_SOURCE"
hla2010_shell_log "CERTI upstream build: $CERTI_UPSTREAM_BUILD"
hla2010_shell_log "CERTI upstream install: $CERTI_UPSTREAM_INSTALL"
hla2010_shell_log "CERTI upstream build log: $build_log"
set +e
HLA2010_CERTI_SOURCE="$CERTI_UPSTREAM_SOURCE" \
HLA2010_CERTI_BUILD="$CERTI_UPSTREAM_BUILD" \
HLA2010_CERTI_PREFIX="$CERTI_UPSTREAM_INSTALL" \
HLA2010_CERTI_CMAKE_ARGS="${HLA2010_CERTI_UPSTREAM_CMAKE_ARGS:--DBUILD_TESTING=OFF}" \
HLA2010_CERTI_BUILD_TARGETS="${HLA2010_CERTI_UPSTREAM_BUILD_TARGETS:-RTI RTI1516 RTI1516e rtig rtia}" \
"$ROOT_DIR/scripts/rebuild_certi.sh" 2>&1 | tee "$build_log"
status="${PIPESTATUS[0]}"
set -e

if [[ "$status" -ne 0 ]]; then
  if grep -q "CertiCheckHostAndIP" "$build_log" \
    && [[ -x "$CERTI_UPSTREAM_INSTALL/bin/rtig" ]] \
    && [[ -x "$CERTI_UPSTREAM_INSTALL/bin/rtia" ]] \
    && [[ -e "$CERTI_UPSTREAM_INSTALL/lib/libRTI1516ed.dylib" ]]; then
    echo "warning: upstream CERTI install skipped missing legacy CertiCheckHostAndIP test utility; runtime baseline artifacts are present" >&2
  else
    exit "$status"
  fi
fi

cat <<EOF
Upstream CERTI baseline ready.

Use this environment for pristine/original CERTI comparison:

export HLA2010_CERTI_UPSTREAM_PREFIX="$CERTI_UPSTREAM_INSTALL"
export HLA2010_CERTI_UPSTREAM_BUILD_ROOT="$CERTI_UPSTREAM_BUILD"
EOF
