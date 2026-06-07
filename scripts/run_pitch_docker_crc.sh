#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
pitch_home="${HLA2010_PITCH_HOME:-}"

# shellcheck source=lib/shell.sh
source "$ROOT_DIR/scripts/lib/shell.sh"
hla2010_shell_init "$0"

usage() {
  cat <<'EOF'
usage: ./scripts/run_pitch_docker_crc.sh [docker-launch-args...]

Build and launch the Docker-backed Pitch CRC runtime using the configured
Pitch installation and seeded user-home state.
EOF
}

case "${1:-}" in
  help|-h|--help)
    usage
    exit 0
    ;;
esac

if [[ -z "$pitch_home" && -d "$ROOT_DIR/third_party/pitch/PITCH-prti1516e-manual" ]]; then
  pitch_home="$ROOT_DIR/third_party/pitch/PITCH-prti1516e-manual"
fi
if [[ -z "$pitch_home" ]]; then
  hla2010_shell_die "Pitch runtime home not found; set HLA2010_PITCH_HOME"
fi

pitch_user_home="$("$ROOT_DIR/scripts/setup_pitch_state.sh")"
image="${HLA2010_PITCH_DOCKER_IMAGE:-hla2010-pitch-prti-free-crc:5.5.10}"
crc_port="${HLA2010_PITCH_CRC_PORT:-8989}"
fedpro_port="${HLA2010_PITCH_FEDPRO_PORT:-15164}"
container_name="${HLA2010_PITCH_DOCKER_NAME:-}"
detach="${HLA2010_PITCH_DOCKER_DETACH:-0}"
host_gateway_arg="$(hla2010_shell_docker_host_gateway_arg || true)"

if [[ "${HLA2010_PITCH_DOCKER_BUILD:-1}" != "0" ]]; then
  hla2010_shell_log "building Pitch Docker image: $image"
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
if [[ -n "$host_gateway_arg" ]]; then
  docker_args+=("$host_gateway_arg")
fi

hla2010_shell_log "launching Pitch Docker container: $image"
exec docker "${docker_args[@]}" \
  -e HOME=/root \
  -e JAVA_OPTS="${HLA2010_PITCH_DOCKER_JAVA_OPTS:--XX:+UseParallelGC -XX:MaxRAMPercentage=75}" \
  -v "$pitch_user_home:/root" \
  -p "127.0.0.1:$crc_port:8989" \
  -p "127.0.0.1:$fedpro_port:15164" \
  "$image"
