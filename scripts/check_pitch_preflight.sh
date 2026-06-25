#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# shellcheck source=lib/shell.sh
source "$ROOT_DIR/scripts/lib/shell.sh"
hla2010_shell_init "$0"

PITCH_BUNDLE_DIR="${HLA2010_PITCH_HOME:-$ROOT_DIR/third_party/pitch/PITCH-prti1516e-manual}"
PITCH_ZIP="${ROOT_DIR}/third_party/pitch/HLA_PITCH_linux.zip"
PITCH_LOCAL_ARCHIVE_DIR="${ROOT_DIR}/third_party/pitch/HLA_PITCH_linux"
CONTAINER_NAME="${HLA2010_PITCH_DOCKER_NAME:-hla2010-pitch-crc}"
IMAGE_NAME="${HLA2010_PITCH_DOCKER_IMAGE:-hla2010-pitch-prti-free-crc:5.5.10}"
CRC_PORT_EXPLICIT=0
FEDPRO_PORT_EXPLICIT=0
if [[ -n "${HLA2010_PITCH_CRC_PORT+x}" ]]; then
  CRC_PORT_EXPLICIT=1
fi
if [[ -n "${HLA2010_PITCH_FEDPRO_PORT+x}" ]]; then
  FEDPRO_PORT_EXPLICIT=1
fi
CRC_PORT="${HLA2010_PITCH_CRC_PORT:-8989}"
FEDPRO_PORT="${HLA2010_PITCH_FEDPRO_PORT:-15164}"
AUTO_PORTS="${HLA2010_PITCH_AUTO_PORTS:-1}"
OUTPUT_JSON=0
OUTPUT_JSON_FILE=""
NEXT_IS_JSON_FILE=0

for arg in "$@"; do
  if [[ "$NEXT_IS_JSON_FILE" -eq 1 ]]; then
    OUTPUT_JSON_FILE="$arg"
    NEXT_IS_JSON_FILE=0
    continue
  fi
  case "$arg" in
    --json)
      OUTPUT_JSON=1
      ;;
    --json-file)
      NEXT_IS_JSON_FILE=1
      ;;
    --json-file=*)
      OUTPUT_JSON_FILE="${arg#*=}"
      ;;
  esac
done

resolve_pitch_home() {
  local python_bin
  python_bin="$(hla2010_shell_python_bin)"
  if [[ -n "${HLA2010_PITCH_HOME:-}" && -d "${HLA2010_PITCH_HOME:-}" ]]; then
    printf '%s\n' "$HLA2010_PITCH_HOME"
    return 0
  fi
  if [[ -n "${HLA2010_PITCH_HOME:-}" ]]; then
    return 1
  fi
  if [[ -d "$ROOT_DIR/third_party/pitch/PITCH-prti1516e-manual" ]]; then
    printf '%s\n' "$ROOT_DIR/third_party/pitch/PITCH-prti1516e-manual"
    return 0
  fi
  if [[ -f "$PITCH_ZIP" ]]; then
    "$python_bin" -m zipfile -e "$PITCH_ZIP" "$ROOT_DIR/third_party/pitch"
  elif [[ -d "$PITCH_LOCAL_ARCHIVE_DIR" ]]; then
    if [[ -d "$PITCH_LOCAL_ARCHIVE_DIR/PITCH-prti1516e-manual" ]]; then
      cp -R "$PITCH_LOCAL_ARCHIVE_DIR/PITCH-prti1516e-manual" "$ROOT_DIR/third_party/pitch/"
    fi
  fi
  if [[ -d "$ROOT_DIR/third_party/pitch/PITCH-prti1516e-manual" ]]; then
    printf '%s\n' "$ROOT_DIR/third_party/pitch/PITCH-prti1516e-manual"
    return 0
  fi
  return 1
}

show_hint() {
  local title="$1"
  local detail="$2"
  printf '[%s] %s: %s\n' "${HLA2010_SCRIPT_NAME:-script}" "$title" "$detail"
}

emit_json_payload() {
  local python_bin
  python_bin="$(hla2010_shell_python_bin)"
  PITCH_STATUS="$status" \
  PITCH_PLATFORM="$platform" \
  PITCH_ENVIRONMENT="$environment" \
  PITCH_RESULT="$result" \
  PITCH_DOCKER_STATUS="$docker_status" \
  PITCH_DOCKER_DETAIL="$docker_detail" \
  PITCH_BUNDLE_STATUS="$bundle_status" \
  PITCH_BUNDLE_DETAIL="$bundle_detail" \
  PITCH_USER_HOME="$user_home_detail" \
  PITCH_CRC_PORT_STATUS="$crc_port_status" \
  PITCH_CRC_PORT_DETAIL="$crc_port_detail" \
  PITCH_FEDPRO_PORT_STATUS="$fedpro_port_status" \
  PITCH_FEDPRO_PORT_DETAIL="$fedpro_port_detail" \
  PITCH_RUNTIME_HOME="$runtime_home_detail" \
  PITCH_RUNTIME_MARKER="$runtime_marker_detail" \
  PITCH_IMAGE_NAME="$IMAGE_NAME" \
  PITCH_CONTAINER_NAME="$CONTAINER_NAME" \
  PITCH_CRC_PORT="$CRC_PORT" \
  PITCH_FEDPRO_PORT="$FEDPRO_PORT" \
  PITCH_NEXT_STEP="$next_step" \
  ROOT_DIR="$ROOT_DIR" \
  "$python_bin" - <<'PY'
import json
import os
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(os.environ.get("ROOT_DIR", ".")).resolve()
TMPDIR = Path(tempfile.gettempdir()).resolve()
TMP_ROOTS = tuple(
    dict.fromkeys(
        [
            str(TMPDIR),
            tempfile.gettempdir(),
            "/tmp",
            "/private/tmp",
            "/var/tmp",
        ]
        + ([f"/private{TMPDIR}"] if str(TMPDIR).startswith("/var/") else [])
    )
)


def render_path(raw: str | None) -> str | None:
    if not raw:
        return raw
    path = Path(raw).expanduser()
    if not path.is_absolute():
        return path.as_posix()
    try:
        resolved = path.resolve()
    except OSError:
        resolved = path
    try:
        return resolved.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        pass
    for root_string in TMP_ROOTS:
        root = Path(root_string)
        try:
            return f"<tmp>/{resolved.relative_to(root).as_posix()}"
        except ValueError:
            continue
    return resolved.as_posix()


def sanitize_text(raw: str | None) -> str | None:
    if raw is None:
        return None
    return raw.replace(str(REPO_ROOT), "<repo>")

payload = {
    "tool": "pitch-preflight",
    "platform": os.environ.get("PITCH_PLATFORM"),
    "environment": os.environ.get("PITCH_ENVIRONMENT"),
    "result": os.environ.get("PITCH_RESULT"),
    "checks": [
        {
            "name": "docker",
            "ok": os.environ.get("PITCH_DOCKER_STATUS") == "ok",
            "status": os.environ.get("PITCH_DOCKER_STATUS"),
            "detail": os.environ.get("PITCH_DOCKER_DETAIL"),
        },
        {
            "name": "pitch_bundle",
            "ok": os.environ.get("PITCH_BUNDLE_STATUS") == "ok",
            "status": os.environ.get("PITCH_BUNDLE_STATUS"),
            "detail": sanitize_text(os.environ.get("PITCH_BUNDLE_DETAIL")),
        },
        {
            "name": "pitch_user_home",
            "ok": bool(os.environ.get("PITCH_USER_HOME")),
            "status": "ok" if os.environ.get("PITCH_USER_HOME") else "missing",
            "detail": render_path(os.environ.get("PITCH_USER_HOME")) or "missing user.home",
        },
        {
            "name": "crc_port",
            "ok": os.environ.get("PITCH_CRC_PORT_STATUS") == "ok",
            "status": os.environ.get("PITCH_CRC_PORT_STATUS"),
            "detail": os.environ.get("PITCH_CRC_PORT_DETAIL"),
        },
        {
            "name": "fedpro_port",
            "ok": os.environ.get("PITCH_FEDPRO_PORT_STATUS") == "ok",
            "status": os.environ.get("PITCH_FEDPRO_PORT_STATUS"),
            "detail": os.environ.get("PITCH_FEDPRO_PORT_DETAIL"),
        },
    ],
    "runtime": {
        "home": render_path(os.environ.get("PITCH_RUNTIME_HOME")),
        "required_marker": render_path(os.environ.get("PITCH_RUNTIME_MARKER")),
        "user_home": render_path(os.environ.get("PITCH_USER_HOME")),
        "image_name": os.environ.get("PITCH_IMAGE_NAME"),
        "container_name": os.environ.get("PITCH_CONTAINER_NAME"),
    },
    "required_markers": {
        "runtime_home": render_path(os.environ.get("PITCH_RUNTIME_MARKER")),
    },
    "ports": {
        "crc": {
            "host": "127.0.0.1",
            "port": int(os.environ.get("PITCH_CRC_PORT", "8989")),
            "status": os.environ.get("PITCH_CRC_PORT_STATUS"),
            "detail": os.environ.get("PITCH_CRC_PORT_DETAIL"),
        },
        "fedpro": {
            "host": "127.0.0.1",
            "port": int(os.environ.get("PITCH_FEDPRO_PORT", "15164")),
            "status": os.environ.get("PITCH_FEDPRO_PORT_STATUS"),
            "detail": os.environ.get("PITCH_FEDPRO_PORT_DETAIL"),
        },
    },
    "next_step": os.environ.get("PITCH_NEXT_STEP"),
    "exit_code": int(os.environ.get("PITCH_STATUS", "1")),
}
json.dump(payload, sys.stdout, indent=2, sort_keys=True)
sys.stdout.write("\n")
PY
}

docker_container_running() {
  docker ps --format '{{.Names}}' | grep -Fxq "$CONTAINER_NAME"
}

check_port_available() {
  local port="$1"
  local python_bin
  python_bin="$(hla2010_shell_python_bin)"
  "$python_bin" - "$port" <<'PY'
import socket
import sys

port = int(sys.argv[1])
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    try:
        sock.bind(("127.0.0.1", port))
        sock.listen(1)
    except OSError as exc:
        print(exc)
        raise SystemExit(1)
raise SystemExit(0)
PY
}

find_available_port() {
  local python_bin
  python_bin="$(hla2010_shell_python_bin)"
  "$python_bin" - "$@" <<'PY'
import socket
import sys

forbidden = {int(item) for item in sys.argv[1:] if item}
for _ in range(128):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        port = int(sock.getsockname()[1])
    if port not in forbidden:
        print(port)
        raise SystemExit(0)
raise SystemExit(1)
PY
}

status=0
platform="$(uname -s -r -m)"
docker_status="ok"
docker_detail="ok"
bundle_status="ok"
bundle_detail="ok"
user_home_detail=""
runtime_home_detail=""
runtime_marker_detail=""
crc_port_status="ok"
crc_port_detail="ok"
fedpro_port_status="ok"
fedpro_port_detail="ok"
managed_container_running=0

if [[ "$OUTPUT_JSON" -eq 0 ]]; then
  hla2010_shell_log "Pitch preflight"
  show_hint "platform" "$platform"
fi

if hla2010_shell_have docker; then
  if docker info >/dev/null 2>&1; then
    docker_detail="ok: $(command -v docker)"
    if docker_container_running; then
      managed_container_running=1
    fi
    if [[ "$OUTPUT_JSON" -eq 0 ]]; then
      show_hint "docker" "$docker_detail"
    fi
  else
    status=1
    docker_status="blocked"
    docker_detail="blocked: Docker CLI exists but the daemon is not reachable"
    if [[ "$OUTPUT_JSON" -eq 0 ]]; then
      show_hint "docker" "$docker_detail"
    fi
  fi
else
  status=1
  docker_status="missing"
  docker_detail="missing: install Docker Desktop or Docker Engine first"
  if [[ "$OUTPUT_JSON" -eq 0 ]]; then
    show_hint "docker" "$docker_detail"
  fi
fi

if resolved_home="$(resolve_pitch_home)"; then
  runtime_home_detail="$resolved_home"
  runtime_marker_detail="$resolved_home/lib/prtifull.jar"
  if [[ -f "$runtime_marker_detail" ]]; then
    bundle_detail="ok: $resolved_home"
    user_home_detail="${HLA2010_PITCH_USER_HOME:-$ROOT_DIR/.local/pitch/user-home}"
    if [[ "$OUTPUT_JSON" -eq 0 ]]; then
      show_hint "pitch bundle" "$bundle_detail"
    fi
  else
    status=1
    bundle_status="blocked"
    bundle_detail="blocked: required runtime marker is missing: $runtime_marker_detail"
    if [[ "$OUTPUT_JSON" -eq 0 ]]; then
      show_hint "pitch bundle" "$bundle_detail"
    fi
  fi
else
  status=1
  bundle_status="blocked"
  if [[ -n "${HLA2010_PITCH_HOME:-}" ]]; then
    bundle_detail="blocked: HLA2010_PITCH_HOME does not point at a Pitch runtime directory: $HLA2010_PITCH_HOME"
  elif [[ -f "$PITCH_ZIP" ]]; then
    bundle_detail="blocked: archive exists at $PITCH_ZIP but extraction failed"
  elif [[ -d "$PITCH_LOCAL_ARCHIVE_DIR" ]]; then
    bundle_detail="blocked: extracted archive exists at $PITCH_LOCAL_ARCHIVE_DIR but $PITCH_BUNDLE_DIR is missing"
  else
    bundle_status="missing"
    bundle_detail="missing: set HLA2010_PITCH_HOME or place HLA_PITCH_linux.zip, HLA_PITCH_linux/, or PITCH-prti1516e-manual/ under third_party/pitch/"
  fi
  if [[ "$OUTPUT_JSON" -eq 0 ]]; then
    show_hint "pitch bundle" "$bundle_detail"
    show_hint "next step" "set HLA2010_PITCH_HOME, or place HLA_PITCH_linux.zip, HLA_PITCH_linux/, or PITCH-prti1516e-manual/ under third_party/pitch/"
  fi
fi

if [[ -d "${resolved_home:-}" && "$bundle_status" == "ok" ]]; then
  user_home_detail="${HLA2010_PITCH_USER_HOME:-$ROOT_DIR/.local/pitch/user-home}"
  if [[ "$OUTPUT_JSON" -eq 0 ]]; then
    show_hint "pitch user home" "ok: $user_home_detail"
  fi
fi

crc_port_check_file="$(mktemp "${TMPDIR:-/tmp}/hla2010_pitch_crc_port_check.XXXXXX")"
fedpro_port_check_file="$(mktemp "${TMPDIR:-/tmp}/hla2010_pitch_fedpro_port_check.XXXXXX")"

if [[ "$managed_container_running" -eq 1 ]]; then
  crc_port_detail="ok: managed container $CONTAINER_NAME is already running on 127.0.0.1:$CRC_PORT"
  fedpro_port_detail="ok: managed container $CONTAINER_NAME is already running on 127.0.0.1:$FEDPRO_PORT"
elif check_port_available "$CRC_PORT" >"$crc_port_check_file" 2>&1; then
  crc_port_detail="ok: 127.0.0.1:$CRC_PORT is available"
elif [[ "$AUTO_PORTS" == "1" && "$CRC_PORT_EXPLICIT" -eq 0 ]]; then
  old_crc_port="$CRC_PORT"
  CRC_PORT="$(find_available_port "$FEDPRO_PORT")"
  crc_port_detail="ok: 127.0.0.1:$old_crc_port was unavailable ($(cat "$crc_port_check_file")); selected alternate 127.0.0.1:$CRC_PORT"
else
  status=1
  crc_port_status="blocked"
  crc_port_detail="blocked: 127.0.0.1:$CRC_PORT is not available: $(cat "$crc_port_check_file")"
fi
rm -f "$crc_port_check_file"

if [[ "$managed_container_running" -eq 1 ]]; then
  :
elif check_port_available "$FEDPRO_PORT" >"$fedpro_port_check_file" 2>&1; then
  fedpro_port_detail="ok: 127.0.0.1:$FEDPRO_PORT is available"
elif [[ "$AUTO_PORTS" == "1" && "$FEDPRO_PORT_EXPLICIT" -eq 0 ]]; then
  old_fedpro_port="$FEDPRO_PORT"
  FEDPRO_PORT="$(find_available_port "$CRC_PORT")"
  fedpro_port_detail="ok: 127.0.0.1:$old_fedpro_port was unavailable ($(cat "$fedpro_port_check_file")); selected alternate 127.0.0.1:$FEDPRO_PORT"
else
  status=1
  fedpro_port_status="blocked"
  fedpro_port_detail="blocked: 127.0.0.1:$FEDPRO_PORT is not available: $(cat "$fedpro_port_check_file")"
fi
rm -f "$fedpro_port_check_file"

if [[ "$OUTPUT_JSON" -eq 0 ]]; then
  show_hint "crc port" "$crc_port_detail"
  show_hint "fedpro port" "$fedpro_port_detail"
fi

environment="ready"
if [[ "$docker_status" != "ok" ]]; then
  environment="docker-blocked"
elif [[ "$bundle_status" != "ok" ]]; then
  environment="bundle-blocked"
elif [[ "$crc_port_status" != "ok" || "$fedpro_port_status" != "ok" ]]; then
  environment="ports-blocked"
fi

result="not ready; fix the blocked prerequisite(s) above and rerun"
next_step="fix the blocked prerequisite(s) above and rerun"
if [[ $status -eq 0 ]]; then
  result="ready to run ./tools/pitch install or ./tools/pitch all"
  next_step="./tools/pitch install or ./tools/pitch all"
fi

if [[ "$OUTPUT_JSON" -eq 1 ]]; then
  if [[ -n "$OUTPUT_JSON_FILE" ]]; then
    emit_json_payload > "$OUTPUT_JSON_FILE"
  fi
  emit_json_payload
  exit "$status"
fi

if [[ -n "$OUTPUT_JSON_FILE" ]]; then
  emit_json_payload > "$OUTPUT_JSON_FILE"
fi

if [[ $status -eq 0 ]]; then
  show_hint "environment" "$environment"
  show_hint "result" "$result"
  show_hint "next step" "$next_step"
else
  show_hint "environment" "$environment"
  show_hint "result" "not ready; fix the blocked prerequisite(s) above and rerun"
fi

exit "$status"
