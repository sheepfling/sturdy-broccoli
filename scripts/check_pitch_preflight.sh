#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# shellcheck source=lib/shell.sh
source "$ROOT_DIR/scripts/lib/shell.sh"
hla2010_shell_init "$0"

PITCH_BUNDLE_DIR="${HLA2010_PITCH_HOME:-$ROOT_DIR/third_party/pitch/PITCH-prti1516e-manual}"
PITCH_ZIP="${ROOT_DIR}/third_party/pitch/HLA_PITCH_linux.zip"
PITCH_LOCAL_ARCHIVE_DIR="${ROOT_DIR}/third_party/pitch/HLA_PITCH_linux"
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
  PITCH_NEXT_STEP="$next_step" \
  "$python_bin" - <<'PY'
import json
import os
import sys

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
            "detail": os.environ.get("PITCH_BUNDLE_DETAIL"),
        },
        {
            "name": "pitch_user_home",
            "ok": bool(os.environ.get("PITCH_USER_HOME")),
            "status": "ok" if os.environ.get("PITCH_USER_HOME") else "missing",
            "detail": os.environ.get("PITCH_USER_HOME") or "missing user.home",
        },
    ],
    "next_step": os.environ.get("PITCH_NEXT_STEP"),
    "exit_code": int(os.environ.get("PITCH_STATUS", "1")),
}
json.dump(payload, sys.stdout, indent=2, sort_keys=True)
sys.stdout.write("\n")
PY
}

status=0
platform="$(uname -s -r -m)"
docker_status="ok"
docker_detail="ok"
bundle_status="ok"
bundle_detail="ok"
user_home_detail=""

if [[ "$OUTPUT_JSON" -eq 0 ]]; then
  hla2010_shell_log "Pitch preflight"
  show_hint "platform" "$platform"
fi

if hla2010_shell_have docker; then
  if docker info >/dev/null 2>&1; then
    docker_detail="ok: $(command -v docker)"
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
  bundle_detail="ok: $resolved_home"
  user_home_detail="${HLA2010_PITCH_USER_HOME:-/private/tmp/hla-2010/pitch-user-home}"
  if [[ "$OUTPUT_JSON" -eq 0 ]]; then
    show_hint "pitch bundle" "$bundle_detail"
  fi
else
  status=1
  bundle_status="blocked"
  if [[ -f "$PITCH_ZIP" ]]; then
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

if [[ -d "${resolved_home:-}" ]]; then
  user_home_detail="${HLA2010_PITCH_USER_HOME:-/private/tmp/hla-2010/pitch-user-home}"
  if [[ "$OUTPUT_JSON" -eq 0 ]]; then
    show_hint "pitch user home" "ok: $user_home_detail"
  fi
fi

environment="ready"
if [[ "$docker_status" != "ok" ]]; then
  environment="docker-blocked"
elif [[ "$bundle_status" != "ok" ]]; then
  environment="bundle-blocked"
fi

result="not ready; fix the blocked prerequisite(s) above and rerun"
next_step="fix the blocked prerequisite(s) above and rerun"
if [[ $status -eq 0 ]]; then
  result="ready to run ./pitch install or ./pitch all"
  next_step="./pitch install or ./pitch all"
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
