#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
CONTAINER_NAME="${HLA2010_PITCH_DOCKER_NAME:-hla2010-pitch-crc}"
IMAGE_NAME="${HLA2010_PITCH_DOCKER_IMAGE:-hla2010-pitch-prti-free-crc:5.5.10}"
CRC_PORT="${HLA2010_PITCH_CRC_PORT:-8989}"
FEDPRO_PORT="${HLA2010_PITCH_FEDPRO_PORT:-15164}"
PREFLIGHT_ARTIFACT_DIR="${HLA2010_PREFLIGHT_ARTIFACT_DIR:-$ROOT_DIR/analysis/preflight_artifacts}"

# shellcheck source=lib/shell.sh
source "$ROOT_DIR/scripts/lib/shell.sh"
hla2010_shell_init "$0"

python_cmd() {
  hla2010_shell_python_bin
}

preflight_pitch_docker() {
  "$ROOT_DIR/scripts/check_pitch_preflight.sh" "$@"
}

pitch_preflight_artifact_path() {
  printf '%s/%s\n' "$PREFLIGHT_ARTIFACT_DIR" "pitch-preflight.json"
}

preflight_has_json_file() {
  local arg
  for arg in "$@"; do
    case "$arg" in
      --json-file|--json-file=*)
        return 0
        ;;
    esac
  done
  return 1
}

run_persisted_pitch_preflight() {
  mkdir -p "$PREFLIGHT_ARTIFACT_DIR"
  local artifact_path
  artifact_path="$(pitch_preflight_artifact_path)"
  if preflight_has_json_file "$@"; then
    preflight_pitch_docker "$@"
  else
    preflight_pitch_docker "$@" --json-file "$artifact_path"
  fi
}

emit_pitch_runtime_reports() {
  "$ROOT_DIR/scripts/ci/emit_vendor_runtime_reports.sh" vendor-green pitch || true
}

require_pitch_preflight() {
  mkdir -p "$PREFLIGHT_ARTIFACT_DIR"
  local artifact_path
  artifact_path="$(pitch_preflight_artifact_path)"
  if preflight_pitch_docker --json-file "$artifact_path"; then
    apply_pitch_preflight_runtime_env "$artifact_path"
    return 0
  else
    return 1
  fi
}

apply_pitch_preflight_runtime_env() {
  local artifact_path="$1"
  local env_file
  env_file="$(mktemp "${TMPDIR:-/tmp}/hla2010_pitch_preflight_env.XXXXXX")"
  "$(python_cmd)" - "$artifact_path" >"$env_file" <<'PY'
import json
import shlex
import sys
from pathlib import Path

payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
ports = payload.get("ports") or {}
runtime = payload.get("runtime") or {}
assignments = {}
if "crc" in ports and "port" in ports["crc"]:
    assignments["HLA2010_PITCH_CRC_PORT"] = str(ports["crc"]["port"])
if "fedpro" in ports and "port" in ports["fedpro"]:
    assignments["HLA2010_PITCH_FEDPRO_PORT"] = str(ports["fedpro"]["port"])
if runtime.get("container_name"):
    assignments["HLA2010_PITCH_DOCKER_NAME"] = str(runtime["container_name"])
for key, value in assignments.items():
    print(f"export {key}={shlex.quote(value)}")
PY
  # shellcheck disable=SC1090
  source "$env_file"
  rm -f "$env_file"
  CRC_PORT="${HLA2010_PITCH_CRC_PORT:-8989}"
  FEDPRO_PORT="${HLA2010_PITCH_FEDPRO_PORT:-15164}"
  CONTAINER_NAME="${HLA2010_PITCH_DOCKER_NAME:-hla2010-pitch-crc}"
}

resolve_pitch_home() {
  local python_bin
  python_bin="$(hla2010_shell_python_bin)"
  if [[ -n "${HLA2010_PITCH_HOME:-}" && -d "${HLA2010_PITCH_HOME:-}" ]]; then
    printf '%s\n' "$HLA2010_PITCH_HOME"
    return 0
  fi
  if [[ -n "${HLA2010_PITCH_HOME:-}" ]]; then
    echo "error: HLA2010_PITCH_HOME does not point at a Pitch runtime directory: $HLA2010_PITCH_HOME" >&2
    return 1
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
  require_pitch_preflight
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
  require_pitch_preflight
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
  hla2010_shell_log "running Pitch smoke"
  "$ROOT_DIR/scripts/ci/vendor_green.sh" pitch-smoke
}

verify_pitch_docker() {
  hla2010_shell_log "running Pitch verify"
  "$ROOT_DIR/scripts/ci/vendor_green.sh" pitch-verify
}

run_best_effort_pitch_profile() {
  local profile="$1"
  local status=0
  if "$ROOT_DIR/scripts/ci/vendor_runtime_smoke.sh" "$profile"; then
    status=0
  else
    status=$?
  fi
  "$ROOT_DIR/scripts/ci/emit_vendor_runtime_reports.sh" vendor-green "$profile" || true
  return "$status"
}

smoke_pitch_docker_best_effort() {
  hla2010_shell_log "running Pitch smoke (best-effort)"
  run_best_effort_pitch_profile pitch-smoke
}

verify_pitch_docker_best_effort() {
  hla2010_shell_log "running Pitch verify (best-effort)"
  run_best_effort_pitch_profile pitch-verify
}

doctor_pitch_docker() {
  local preflight_json
  local python_bin
  local pitch_home
  local pitch_user_home
  local docker_ready=0
  preflight_json="$("$ROOT_DIR/scripts/check_pitch_preflight.sh" --json || true)"
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
  if [[ -n "$preflight_json" ]]; then
    python_bin="$(hla2010_shell_python_bin)"
    "$python_bin" - "$preflight_json" <<'PY'
import json
import sys

payload = json.loads(sys.argv[1])
environment = payload.get("environment", "unknown")
result = payload.get("result", "unknown")
next_step = payload.get("next_step", "./tools/pitch preflight")
print(f"environment: {environment}")
print(f"result: {result}")
print(f"next step: {next_step}")
PY
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
  local script_name="./tools/pitch"
  cat <<EOF
usage: $script_name [preflight|install|start|stop|restart|status|logs|smoke|smoke-best-effort|verify|verify-best-effort|all|doctor]

Simple Pitch Docker workflow:
  $script_name preflight [--json] # check Docker and Pitch runtime prerequisites
  $script_name install   # discover runtime, seed user.home, build the image
  $script_name start     # start CRC + FedPro in Docker and wait for ports
  $script_name smoke     # run the real Pitch smoke test
  $script_name smoke-best-effort # run Pitch smoke and treat blocked local preflight as report-only
  $script_name verify    # run the full real Pitch backend matrix
  $script_name verify-best-effort # run Pitch verify and treat blocked local preflight as report-only
  $script_name save-restore # report the current real Pitch save/restore gap profile
  $script_name save-restore-probe # run the current narrow real Pitch save/restore probe
  $script_name save-restore-review [repeat-count] # run repeated review for the real Pitch save/restore probe
  $script_name ddm       # report the current real Pitch DDM gap profile
  $script_name ddm-probe # run the current narrow real Pitch DDM probe
  $script_name ddm-review [repeat-count] # run repeated review for the real Pitch DDM probe
  $script_name negotiated # report the current real Pitch negotiated-ownership gap profile
  $script_name negotiated-probe # run the current narrow real Pitch negotiated-ownership probe
  $script_name negotiated-review [repeat-count] # run repeated review for the real Pitch negotiated-ownership probe
  $script_name lost-federate # report the current real Pitch lost-federate gap profile
  $script_name lost-federate-probe # run the current narrow real Pitch lost-federate probe
  $script_name lost-federate-review [repeat-count] # run repeated review for the real Pitch lost-federate probe
  $script_name crc-macos-repro [args...] # run the macOS CRC startup reproducer
  $script_name crc-docker-repro # run the Docker CRC startup reproducer
  $script_name all       # install, then smoke, then verify
  $script_name logs      # show container logs
  $script_name stop      # stop and remove the container
EOF
}

case "${1:-start}" in
  help|-h|--help)
    usage
    ;;
  preflight)
    preflight_status=0
    if run_persisted_pitch_preflight "${@:2}"; then
      preflight_status=0
    else
      preflight_status=$?
    fi
    emit_pitch_runtime_reports
    exit "$preflight_status"
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
  smoke-best-effort)
    smoke_pitch_docker_best_effort
    ;;
  verify)
    verify_pitch_docker
    ;;
  verify-best-effort)
    verify_pitch_docker_best_effort
    ;;
  save-restore)
    "$ROOT_DIR/scripts/ci/vendor_green.sh" pitch-save-restore
    ;;
  save-restore-probe)
    "$ROOT_DIR/scripts/ci/vendor_green.sh" pitch-save-restore-probe
    ;;
  save-restore-review)
    bash "$ROOT_DIR/scripts/ci/vendor_probe_review.sh" pitch-save-restore-probe "${2:-5}"
    ;;
  ddm)
    "$ROOT_DIR/scripts/ci/vendor_green.sh" pitch-ddm
    ;;
  ddm-probe)
    "$ROOT_DIR/scripts/ci/vendor_green.sh" pitch-ddm-probe
    ;;
  ddm-review)
    bash "$ROOT_DIR/scripts/ci/vendor_probe_review.sh" pitch-ddm-probe "${2:-5}"
    ;;
  negotiated)
    "$ROOT_DIR/scripts/ci/vendor_green.sh" pitch-negotiated
    ;;
  negotiated-probe)
    "$ROOT_DIR/scripts/ci/vendor_green.sh" pitch-negotiated-probe
    ;;
  negotiated-review)
    bash "$ROOT_DIR/scripts/ci/vendor_probe_review.sh" pitch-negotiated-probe "${2:-5}"
    ;;
  lost-federate)
    "$ROOT_DIR/scripts/ci/vendor_green.sh" pitch-lost-federate
    ;;
  lost-federate-probe)
    "$ROOT_DIR/scripts/ci/vendor_green.sh" pitch-lost-federate-probe
    ;;
  lost-federate-review)
    bash "$ROOT_DIR/scripts/ci/vendor_probe_review.sh" pitch-lost-federate-probe "${2:-5}"
    ;;
  crc-macos-repro)
    shift
    exec "$(hla2010_shell_python_bin)" "$ROOT_DIR/scripts/repro_pitch_crc_macos.py" "$@"
    ;;
  crc-docker-repro)
    shift
    exec "$(hla2010_shell_python_bin)" "$ROOT_DIR/scripts/repro_pitch_crc_docker.py" "$@"
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
