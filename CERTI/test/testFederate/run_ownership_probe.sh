#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "usage: $0 <deny|confirm|ifwanted> [federation-name]" >&2
  exit 2
fi

action="$1"
federation_name="${2:-certi-ownership-probe}"

case "$action" in
  deny|confirm|ifwanted)
    ;;
  *)
    echo "error: action must be one of deny, confirm, ifwanted" >&2
    exit 2
    ;;
esac

script_dir="$(cd "$(dirname "$0")" && pwd)"
repo_root="$(cd "$script_dir/../.." && pwd)"
build_root="${CERTI_BUILD_ROOT:-$repo_root-build}"
log_dir="${CERTI_PROBE_LOG_DIR:-$script_dir/logs}"
mkdir -p "$log_dir"
marker_dir="${CERTI_PROBE_MARKER_DIR:-$log_dir/markers-$$}"
mkdir -p "$marker_dir"

tcp_port="${CERTI_TCP_PORT:-19100}"
udp_port="${CERTI_UDP_PORT:-19200}"
host="${CERTI_HOST:-127.0.0.1}"
fom_path="${CERTI_PROBE_FOM:-$repo_root/xml/ieee1516-2010/1516_2-2010/RestaurantFOMmodule.xml}"
object_name="${CERTI_PROBE_OBJECT_NAME:-probe-object}"
rtig_log="$log_dir/rtig-${action}-$$.log"
owner_log="$log_dir/owner-${action}-$$.log"
acquirer_log="$log_dir/acquirer-${action}-$$.log"
owner_registered_marker="$marker_dir/owner-registered"
owner_divesting_marker="$marker_dir/owner-divesting"
acquirer_discovered_marker="$marker_dir/acquirer-discovered"
acquirer_requested_marker="$marker_dir/acquirer-requested"

lib_path="$build_root/libRTI/ieee1516-2010:$build_root/libCERTI:$build_root/libHLA${DYLD_LIBRARY_PATH:+:$DYLD_LIBRARY_PATH}"
rtia_wrapper="${CERTI_RTIA:-$script_dir/rtia_verbose_wrapper.sh}"

cleanup() {
  if [[ -n "${rtig_pid:-}" ]]; then
    kill "$rtig_pid" >/dev/null 2>&1 || true
    wait "$rtig_pid" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

export CERTI_BUILD_ROOT="$build_root"
export CERTI_HOST="$host"
export CERTI_TCP_PORT="$tcp_port"
export CERTI_UDP_PORT="$udp_port"
export CERTI_RTIA="$rtia_wrapper"
export CERTI_PROBE_LOG_DIR="$log_dir"
export CERTI_PROBE_OWNER_REGISTERED_MARKER="$owner_registered_marker"
export CERTI_PROBE_OWNER_DIVESTING_MARKER="$owner_divesting_marker"
export CERTI_PROBE_ACQUIRER_DISCOVERED_MARKER="$acquirer_discovered_marker"
export CERTI_PROBE_ACQUIRER_REQUESTED_MARKER="$acquirer_requested_marker"
export DYLD_LIBRARY_PATH="$lib_path"

"$build_root/RTIG/rtig" -v 4 >"$rtig_log" 2>&1 &
rtig_pid=$!
sleep 1

"$build_root/test/testFederate/CertiOwnershipProbe-IEEE1516_2010" \
  owner "$federation_name" "$fom_path" "$object_name" "$action" >"$owner_log" 2>&1 &
owner_pid=$!

sleep 1

"$build_root/test/testFederate/CertiOwnershipProbe-IEEE1516_2010" \
  acquirer "$federation_name" "$fom_path" "$object_name" >"$acquirer_log" 2>&1 || acquirer_status=$?

owner_status=0
wait "$owner_pid" || owner_status=$?

echo "rtig_log=$rtig_log"
echo "owner_log=$owner_log"
echo "acquirer_log=$acquirer_log"
echo "owner_status=$owner_status"
echo "acquirer_status=${acquirer_status:-0}"

if [[ $owner_status -ne 0 || ${acquirer_status:-0} -ne 0 ]]; then
  exit 1
fi
