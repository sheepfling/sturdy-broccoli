#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "usage: $0 <-p port|-f fd ...>" >&2
  exit 2
fi

script_dir="$(cd "$(dirname "$0")" && pwd)"
repo_root="$(cd "$script_dir/../.." && pwd)"
build_root="${CERTI_BUILD_ROOT:-${repo_root}-build}"
log_dir="${CERTI_PROBE_LOG_DIR:-$script_dir/logs}"
mkdir -p "$log_dir"

timestamp="$(date +%Y%m%d-%H%M%S)"
log_file="$log_dir/rtia-${timestamp}-$$.log"

lib_path="$build_root/libRTI/ieee1516-2010:$build_root/libCERTI:$build_root/libHLA${DYLD_LIBRARY_PATH:+:$DYLD_LIBRARY_PATH}"
export DYLD_LIBRARY_PATH="$lib_path"

echo "[wrapper] exec $build_root/RTIA/rtia $*" >> "$log_file"
exec "$build_root/RTIA/rtia" -v 4 "$@" >>"$log_file" 2>&1
