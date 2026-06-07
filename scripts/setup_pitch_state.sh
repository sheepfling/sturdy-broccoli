#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
HLA2010_LOCAL_STATE_ROOT="${HLA2010_LOCAL_STATE_ROOT:-/private/tmp/hla-2010}"
pitch_home="${HLA2010_PITCH_HOME:-}"

# shellcheck source=lib/shell.sh
source "$ROOT_DIR/scripts/lib/shell.sh"
hla2010_shell_init "$0"

log_err() {
  hla2010_shell_log "$*" >&2
}

if [[ -z "$pitch_home" && -d "$ROOT_DIR/third_party/pitch/PITCH-prti1516e-manual" ]]; then
  pitch_home="$ROOT_DIR/third_party/pitch/PITCH-prti1516e-manual"
fi
if [[ -z "$pitch_home" ]]; then
  hla2010_shell_die "Pitch runtime home not found; set HLA2010_PITCH_HOME"
fi

pitch_user_home="${HLA2010_PITCH_USER_HOME:-$HLA2010_LOCAL_STATE_ROOT/pitch-user-home}"
source_user_home="$pitch_home/user.home"
marker_path="$pitch_user_home/.hla2010_pitch_user_home_seeded"

log_err "seeding Pitch user home at $pitch_user_home"
mkdir -p "$pitch_user_home"

if [[ ! -e "$marker_path" ]]; then
  if [[ -d "$source_user_home" && ! -d "$pitch_user_home/prti1516e" ]]; then
    cp -R "$source_user_home/." "$pitch_user_home/"
  fi
  printf 'seeded-from=%s\n' "$source_user_home" > "$marker_path"
fi

runtime_state_dir="$pitch_user_home/prti1516e"
mkdir -p "$runtime_state_dir"

upsert_setting() {
  local settings_file="$1"
  local key="$2"
  local value="$3"

  if [[ -f "$settings_file" ]]; then
    if grep -Eq "^[[:space:]]*${key//./\\.}=" "$settings_file"; then
      perl -0pi -e "s/^[ \\t]*\\Q$key\\E=.*/$key=$value/m" "$settings_file"
    else
      printf '\n%s=%s\n' "$key" "$value" >> "$settings_file"
    fi
  else
    printf '%s=%s\n' "$key" "$value" > "$settings_file"
  fi
}

common_settings="$runtime_state_dir/prti_common.settings"
if [[ -f "$common_settings" ]]; then
  if grep -Eq '^[[:space:]]*accepted[[:space:]]*=' "$common_settings"; then
    perl -0pi -e 's/^[ \t]*accepted[ \t]*=.*/accepted = true/m' "$common_settings"
  else
    printf '\naccepted = true\n' >> "$common_settings"
  fi
else
  printf 'accepted = true\n' > "$common_settings"
fi

crc_settings="$runtime_state_dir/prti1516eCRC.settings"
upsert_setting "$crc_settings" "CRC.requireWebViewPassPhrase" "false"
upsert_setting "$crc_settings" "CRC.webViewPassPhrase" ""

if [[ "${HLA2010_PITCH_CRC_MODE:-local}" == "docker" ]]; then
  log_err "configuring Pitch user home for Docker mode"
  upsert_setting "$crc_settings" "CRC.skipConnectivityCheck" "true"

  lrc_settings="$runtime_state_dir/prti1516eLRC.settings"
  upsert_setting "$lrc_settings" "LRC.TCP.advertise.mode" "User"
  upsert_setting "$lrc_settings" "LRC.TCP.advertise.address" "${HLA2010_PITCH_LRC_ADVERTISE_ADDRESS:-host.docker.internal}"
  upsert_setting "$lrc_settings" "LRC.TCP.port-range.start" "${HLA2010_PITCH_LRC_TCP_PORT_START:-6010}"
  upsert_setting "$lrc_settings" "LRC.TCP.port-range.end" "${HLA2010_PITCH_LRC_TCP_PORT_END:-6099}"
  upsert_setting "$lrc_settings" "LRC.TCP.port-range.allow-fallback" "false"
  upsert_setting "$lrc_settings" "LRC.UDP.port-range.start" "${HLA2010_PITCH_LRC_UDP_PORT_START:-5010}"
  upsert_setting "$lrc_settings" "LRC.UDP.port-range.end" "${HLA2010_PITCH_LRC_UDP_PORT_END:-5099}"
  upsert_setting "$lrc_settings" "LRC.UDP.port-range.allow-fallback" "false"
  upsert_setting "$lrc_settings" "LRC.skipConnectivityCheck" "true"
fi

mkdir -p "$pitch_user_home/.cache"
printf '%s\n' "$pitch_user_home"
