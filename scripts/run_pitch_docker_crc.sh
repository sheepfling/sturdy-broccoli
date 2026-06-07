#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
pitch_home="${HLA2010_PITCH_HOME:-}"

if [[ -z "$pitch_home" && -d "$ROOT_DIR/third_party/pitch/PITCH-prti1516e-manual" ]]; then
  pitch_home="$ROOT_DIR/third_party/pitch/PITCH-prti1516e-manual"
fi
if [[ -z "$pitch_home" ]]; then
  echo "error: Pitch runtime home not found; set HLA2010_PITCH_HOME" >&2
  exit 1
fi

pitch_user_home="$("$ROOT_DIR/scripts/setup_pitch_state.sh")"
image="${HLA2010_PITCH_DOCKER_IMAGE:-hla2010-pitch-prti-free-crc:5.5.10}"
crc_port="${HLA2010_PITCH_CRC_PORT:-8989}"
fedpro_port="${HLA2010_PITCH_FEDPRO_PORT:-15164}"
container_name="${HLA2010_PITCH_DOCKER_NAME:-}"
detach="${HLA2010_PITCH_DOCKER_DETACH:-0}"

if [[ "${HLA2010_PITCH_DOCKER_BUILD:-1}" != "0" ]]; then
  docker build \
    -t "$image" \
    -f "$ROOT_DIR/scripts/pitch_crc_free.Dockerfile" \
    "$pitch_home"
fi

docker_args=(run --rm --init)
if [[ -n "$container_name" ]]; then
  docker_args+=(--name "$container_name")
fi
if [[ "$detach" != "0" ]]; then
  docker_args+=(-d)
fi

exec docker "${docker_args[@]}" \
  -e HOME=/root \
  -e JAVA_OPTS="${HLA2010_PITCH_DOCKER_JAVA_OPTS:--XX:+UseParallelGC -XX:MaxRAMPercentage=75}" \
  -v "$pitch_user_home:/root" \
  -p "127.0.0.1:$crc_port:8989" \
  -p "127.0.0.1:$fedpro_port:15164" \
  "$image"
