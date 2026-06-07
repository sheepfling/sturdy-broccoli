#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
CONTAINER_NAME="${HLA2010_PITCH_DOCKER_NAME:-hla2010-pitch-crc}"
IMAGE_NAME="${HLA2010_PITCH_DOCKER_IMAGE:-hla2010-pitch-prti-free-crc:5.5.10}"
CRC_PORT="${HLA2010_PITCH_CRC_PORT:-8989}"
FEDPRO_PORT="${HLA2010_PITCH_FEDPRO_PORT:-15164}"

# shellcheck source=lib/shell.sh
source "$ROOT_DIR/scripts/lib/shell.sh"
hla2010_shell_init "$0"

python_cmd() {
  hla2010_shell_python_bin
}

resolve_pitch_home() {
  local python_bin
  python_bin="$(hla2010_shell_python_bin)"
  if [[ -n "${HLA2010_PITCH_HOME:-}" && -d "${HLA2010_PITCH_HOME:-}" ]]; then
    printf '%s\n' "$HLA2010_PITCH_HOME"
    return 0
  fi
  if [[ -d "$ROOT_DIR/third_party/pitch/PITCH-prti1516e-manual" ]]; then
    printf '%s\n' "$ROOT_DIR/third_party/pitch/PITCH-prti1516e-manual"
    return 0
  fi
  if [[ -f "$ROOT_DIR/third_party/pitch/HLA_PITCH_linux.zip" ]]; then
    "$python_bin" -m zipfile -e "$ROOT_DIR/third_party/pitch/HLA_PITCH_linux.zip" "$ROOT_DIR/third_party/pitch"
  elif [[ -d "$ROOT_DIR/third_party/pitch/HLA_PITCH_linux" ]]; then
    if [[ -d "$ROOT_DIR/third_party/pitch/HLA_PITCH_linux/PITCH-prti1516e-manual" ]]; then
      cp -R "$ROOT_DIR/third_party/pitch/HLA_PITCH_linux/PITCH-prti1516e-manual" "$ROOT_DIR/third_party/pitch/"
    fi
  fi
  if [[ -d "$ROOT_DIR/third_party/pitch/PITCH-prti1516e-manual" ]]; then
    printf '%s\n' "$ROOT_DIR/third_party/pitch/PITCH-prti1516e-manual"
    return 0
  fi
  echo "error: Pitch runtime bundle not found." >&2
  echo "Put the extracted vendor runtime at third_party/pitch/PITCH-prti1516e-manual" >&2
  echo "or set HLA2010_PITCH_HOME." >&2
  return 1
}

resolve_pitch_user_home() {
  HLA2010_PITCH_HOME="$(resolve_pitch_home)" "$ROOT_DIR/scripts/setup_pitch_state.sh"
}

wait_for_port() {
  local host="$1"
  local port="$2"
  local timeout="$3"
  local python_bin
  python_bin="$(python_cmd)"
  "$python_bin" - "$host" "$port" "$timeout" <<'PY'
import socket
import sys
import time

host = sys.argv[1]
port = int(sys.argv[2])
timeout = float(sys.argv[3])
deadline = time.time() + timeout
while time.time() < deadline:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.2)
        if sock.connect_ex((host, port)) == 0:
            raise SystemExit(0)
    time.sleep(0.2)
raise SystemExit(1)
PY
}

docker_container_exists() {
  docker ps -a --format '{{.Names}}' | grep -Fxq "$CONTAINER_NAME"
}

docker_container_running() {
  docker ps --format '{{.Names}}' | grep -Fxq "$CONTAINER_NAME"
}

ensure_docker_daemon() {
  hla2010_shell_have docker || hla2010_shell_die "docker CLI not found"
  docker info >/dev/null
}

install_pitch_docker() {
  local pitch_home
  local pitch_user_home
  pitch_home="$(resolve_pitch_home)"
  pitch_user_home="$(resolve_pitch_user_home)"
  hla2010_shell_log "Pitch runtime: $pitch_home"
  hla2010_shell_log "Pitch user home: $pitch_user_home"
  ensure_docker_daemon
  docker build \
    -t "$IMAGE_NAME" \
    -f "$ROOT_DIR/scripts/pitch_crc_free.Dockerfile" \
    "$pitch_home"
  docker image inspect "$IMAGE_NAME" >/dev/null
  hla2010_shell_log "Pitch Docker image ready: $IMAGE_NAME"
}

start_pitch_docker() {
  local pitch_home
  local pitch_user_home
  pitch_home="$(resolve_pitch_home)"
  pitch_user_home="$(resolve_pitch_user_home)"
  ensure_docker_daemon
  docker image inspect "$IMAGE_NAME" >/dev/null 2>&1 || install_pitch_docker
  if docker_container_running; then
    hla2010_shell_log "Pitch Docker already running: $CONTAINER_NAME"
    return 0
  fi
  if docker_container_exists; then
    docker rm -f "$CONTAINER_NAME" >/dev/null
  fi
  HLA2010_PITCH_HOME="$pitch_home" \
  HLA2010_PITCH_USER_HOME="$pitch_user_home" \
  HLA2010_PITCH_CRC_MODE=docker \
  HLA2010_PITCH_DOCKER_IMAGE="$IMAGE_NAME" \
  HLA2010_PITCH_DOCKER_BUILD=0 \
  HLA2010_PITCH_DOCKER_NAME="$CONTAINER_NAME" \
  HLA2010_PITCH_DOCKER_DETACH=1 \
  "$ROOT_DIR/scripts/run_pitch_docker_crc.sh" >/dev/null
  wait_for_port 127.0.0.1 "$CRC_PORT" 45
  wait_for_port 127.0.0.1 "$FEDPRO_PORT" 45
  hla2010_shell_log "Pitch Docker running: $CONTAINER_NAME"
  hla2010_shell_log "CRC:    127.0.0.1:$CRC_PORT"
  hla2010_shell_log "FedPro: 127.0.0.1:$FEDPRO_PORT"
}

stop_pitch_docker() {
  ensure_docker_daemon
  if docker_container_exists; then
    docker rm -f "$CONTAINER_NAME" >/dev/null
    hla2010_shell_log "Stopped: $CONTAINER_NAME"
  else
    hla2010_shell_log "Pitch Docker is not running."
  fi
}

status_pitch_docker() {
  local pitch_home
  local pitch_user_home
  pitch_home="$(resolve_pitch_home)"
  pitch_user_home="$(resolve_pitch_user_home)"
  hla2010_shell_log "Pitch runtime: $pitch_home"
  hla2010_shell_log "Pitch user home: $pitch_user_home"
  hla2010_shell_log "Image: $IMAGE_NAME"
  hla2010_shell_log "Container: $CONTAINER_NAME"
  if docker_container_running; then
    hla2010_shell_log "Status: running"
    docker ps --filter "name=^${CONTAINER_NAME}$" --format 'Ports: {{.Ports}}'
  elif docker_container_exists; then
    hla2010_shell_log "Status: stopped"
  else
    hla2010_shell_log "Status: not created"
  fi
}

logs_pitch_docker() {
  ensure_docker_daemon
  if ! docker_container_exists; then
    hla2010_shell_warn "Pitch Docker container does not exist."
    return 1
  fi
  docker logs "$CONTAINER_NAME"
}

smoke_pitch_docker() {
  local pitch_home
  local pitch_user_home
  local python_bin
  pitch_home="$(resolve_pitch_home)"
  pitch_user_home="$(resolve_pitch_user_home)"
  python_bin="$(python_cmd)"
  ensure_docker_daemon
  docker image inspect "$IMAGE_NAME" >/dev/null 2>&1 || install_pitch_docker
  if docker_container_running; then
    stop_pitch_docker
  fi
  hla2010_shell_log "running Pitch smoke"
  export HLA2010_ENABLE_REAL_RTI_SMOKE=1
  export HLA2010_PITCH_HOME="$pitch_home"
  export HLA2010_PITCH_USER_HOME="$pitch_user_home"
  export HLA2010_PITCH_CRC_MODE=docker
  export HLA2010_PITCH_DOCKER_BUILD=0
  hla2010_shell_log "python: $python_bin"
  "$python_bin" -m pytest -q tests/vendors/test_real_vendor_runtime_smoke.py -k pitch -rs
}

verify_pitch_docker() {
  local pitch_home
  local pitch_user_home
  local python_bin
  pitch_home="$(resolve_pitch_home)"
  pitch_user_home="$(resolve_pitch_user_home)"
  python_bin="$(python_cmd)"
  ensure_docker_daemon
  docker image inspect "$IMAGE_NAME" >/dev/null 2>&1 || install_pitch_docker
  if docker_container_running; then
    stop_pitch_docker
  fi
  hla2010_shell_log "running Pitch verify"
  export HLA2010_ENABLE_REAL_RTI_SMOKE=1
  export HLA2010_PITCH_HOME="$pitch_home"
  export HLA2010_PITCH_USER_HOME="$pitch_user_home"
  export HLA2010_PITCH_CRC_MODE=docker
  export HLA2010_PITCH_DOCKER_BUILD=0
  hla2010_shell_log "python: $python_bin"
  "$python_bin" -m pytest -q tests/vendors/test_pitch_real_backend_matrix.py -rs
}

doctor_pitch_docker() {
  local pitch_home
  local pitch_user_home
  local docker_ready=0
  pitch_home="$(resolve_pitch_home)"
  pitch_user_home="$(resolve_pitch_user_home)"
  hla2010_shell_log "Pitch runtime: $pitch_home"
  hla2010_shell_log "Pitch user home: $pitch_user_home"
  if hla2010_shell_have docker; then
    hla2010_shell_log "Docker CLI: $(command -v docker)"
    if docker info >/dev/null 2>&1; then
      hla2010_shell_log "Docker daemon: reachable"
      docker_ready=1
    else
      hla2010_shell_warn "Docker daemon: not reachable"
    fi
  else
    hla2010_shell_warn "Docker CLI: missing"
  fi
  if [[ "$docker_ready" -eq 1 ]]; then
    if docker image inspect "$IMAGE_NAME" >/dev/null 2>&1; then
      hla2010_shell_log "Image: present ($IMAGE_NAME)"
    else
      hla2010_shell_warn "Image: missing ($IMAGE_NAME)"
    fi
    if docker_container_running; then
      hla2010_shell_log "Container: running ($CONTAINER_NAME)"
    elif docker_container_exists; then
      hla2010_shell_log "Container: stopped ($CONTAINER_NAME)"
    else
      hla2010_shell_log "Container: absent ($CONTAINER_NAME)"
    fi
  else
    hla2010_shell_warn "Skipping container/image checks because Docker is unavailable"
  fi
}

usage() {
  local script_name="${HLA2010_SCRIPT_NAME:-$(basename "$0")}"
  cat <<EOF
usage: $script_name [install|start|stop|restart|status|logs|smoke|verify|all|doctor]

Simple Pitch Docker workflow:
  $script_name install   # discover runtime, seed user.home, build the image
  $script_name start     # start CRC + FedPro in Docker and wait for ports
  $script_name smoke     # run the real Pitch smoke test
  $script_name verify    # run the full real Pitch backend matrix
  $script_name all       # install, then smoke, then verify
  $script_name logs      # show container logs
  $script_name stop      # stop and remove the container
EOF
}

case "${1:-start}" in
  help|-h|--help)
    usage
    ;;
  install)
    install_pitch_docker
    ;;
  start)
    start_pitch_docker
    ;;
  stop)
    stop_pitch_docker
    ;;
  restart)
    stop_pitch_docker || true
    start_pitch_docker
    ;;
  status)
    status_pitch_docker
    ;;
  logs)
    logs_pitch_docker
    ;;
  smoke)
    smoke_pitch_docker
    ;;
  verify)
    verify_pitch_docker
    ;;
  all)
    install_pitch_docker
    smoke_pitch_docker
    verify_pitch_docker
    ;;
  doctor)
    doctor_pitch_docker
    ;;
  *)
    usage
    exit 2
    ;;
esac
