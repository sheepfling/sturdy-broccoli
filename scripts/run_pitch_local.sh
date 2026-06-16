#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
pitch_home="${HLA2010_PITCH_HOME:-}"
pitch_java_home="${HLA2010_PITCH_JAVA_HOME:-}"
pitch_java_bin="${HLA2010_PITCH_JAVA_BIN:-}"
launcher_mode="${HLA2010_PITCH_LAUNCHER_MODE:-raw}"

# shellcheck source=lib/shell.sh
source "$ROOT_DIR/scripts/lib/shell.sh"
# shellcheck disable=SC1091
source "$ROOT_DIR/scripts/local_state.sh"
hla2010_shell_init "$0"

usage() {
  cat <<'EOF'
usage: ./scripts/run_pitch_local.sh [pitch-launch-args...]

Launch the local Pitch runtime using the configured Pitch installation and
user-home state.
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

pitch_user_home="${HLA2010_PITCH_USER_HOME:-$(local_state_path "pitch-user-home")}"
prti_jar="$pitch_home/lib/prtifull.jar"

if [[ -n "$pitch_java_bin" && -x "$pitch_java_bin" ]]; then
  java_bin="$pitch_java_bin"
elif [[ -n "$pitch_java_home" && -x "$pitch_java_home/bin/java" ]]; then
  java_bin="$pitch_java_home/bin/java"
elif [[ -x "$pitch_home/Contents/Home/bin/java" ]]; then
  java_bin="$pitch_home/Contents/Home/bin/java"
elif [[ -x "$pitch_home/jre/bin/java" ]]; then
  java_bin="$pitch_home/jre/bin/java"
elif [[ -x "$pitch_home/.install4j/jre.bundle/Contents/Home/bin/java" ]]; then
  java_bin="$pitch_home/.install4j/jre.bundle/Contents/Home/bin/java"
else
  hla2010_shell_die "bundled Java runtime not found below $pitch_home"
fi

java_library_parts=("$pitch_home/lib")
if [[ -d "$pitch_home/.i4j_external_12081/lib" ]]; then
  java_library_parts+=("$pitch_home/.i4j_external_12081/lib")
fi
if [[ -d "$pitch_home/.i4j_external_12081/lib/clang12" ]]; then
  java_library_parts+=("$pitch_home/.i4j_external_12081/lib/clang12")
fi
if [[ -d "$pitch_home/lib/clang12" ]]; then
  java_library_parts+=("$pitch_home/lib/clang12")
fi
java_library_path="$(IFS=:; echo "${java_library_parts[*]}")"
jvm_args=(-Xmx512m)
if [[ "$(uname -s)" == "Darwin" ]]; then
  # Pitch's bundled JVM can abort during AppKit registration unless macOS starts it on the first thread.
  jvm_args=(-XstartOnFirstThread "${jvm_args[@]}")
fi
if [[ -n "${HLA2010_PITCH_JVM_ARGS:-}" ]]; then
  read -r -a extra_jvm_args <<< "${HLA2010_PITCH_JVM_ARGS}"
  jvm_args+=("${extra_jvm_args[@]}")
fi

pitch_user_home="$("$ROOT_DIR/scripts/setup_pitch_state.sh")"
pidfile="$pitch_user_home/.hla2010_pitch_crc.pid"
common_settings="$pitch_user_home/prti1516e/prti_common.settings"

resolve_install4j_user_home() {
  local real_home="$1"
  case "$real_home" in
    *" "*)
      local link_root="${TMPDIR:-/tmp}/hla-pitch-user-home-links"
      mkdir -p "$link_root"
      local digest
      digest="$(printf '%s' "$real_home" | shasum | awk '{print $1}')"
      local alias_path="$link_root/$digest"
      rm -f "$alias_path"
      ln -s "$real_home" "$alias_path"
      printf '%s\n' "$alias_path"
      ;;
    *)
      printf '%s\n' "$real_home"
      ;;
  esac
}

hla2010_shell_log "Pitch runtime: $pitch_home"
hla2010_shell_log "Pitch user home: $pitch_user_home"
hla2010_shell_log "Pitch launcher mode: $launcher_mode"

mkdir -p "$pitch_user_home/prti1516e"

if [[ -f "$common_settings" ]]; then
  if grep -Eq '^[[:space:]]*accepted[[:space:]]*=' "$common_settings"; then
    perl -0pi -e 's/^[ \t]*accepted[ \t]*=.*/accepted = true/m' "$common_settings"
  else
    printf '\naccepted = true\n' >> "$common_settings"
  fi
else
  printf 'accepted = true\n' > "$common_settings"
fi

if [[ "${HLA2010_PITCH_UI_AUTOMATION:-0}" != "0" ]] && [[ "$(uname -s)" == "Darwin" ]]; then
  hla2010_shell_log "starting macOS Pitch dialog automation helper"
  bash "$ROOT_DIR/scripts/accept_pitch_dialog.sh" >/dev/null 2>&1 &
fi

if [[ -f "$pidfile" ]]; then
  old_pid="$(cat "$pidfile" 2>/dev/null || true)"
  if [[ -n "${old_pid:-}" ]] && ps -p "$old_pid" > /dev/null 2>&1; then
    old_command="$(ps -p "$old_pid" -o command= || true)"
    if [[ "$old_command" == *"prtifull.jar"* || "$old_command" == *"install4j.se.pitch.prti1516e.RTIexec"* ]]; then
      kill "$old_pid" 2>/dev/null || true
      for _ in {1..50}; do
        if ! ps -p "$old_pid" > /dev/null 2>&1; then
          break
        fi
        sleep 0.1
      done
    fi
  fi
fi

if [[ $# -eq 0 ]]; then
  set -- -nogui -verbose
fi

printf '%s\n' "$$" > "$pidfile"
case "$launcher_mode" in
  raw)
    hla2010_shell_log "launching Pitch via raw java jar"
    exec env HOME="$pitch_user_home" \
      "$java_bin" \
      "${jvm_args[@]}" \
      -Duser.home="$pitch_user_home" \
      -Djava.library.path="$java_library_path" \
      -jar "$prti_jar" \
      -nocmdline \
      "$@"
    ;;
  install4j)
    hla2010_shell_log "launching Pitch via install4j cmdline"
    install4j_launcher="$pitch_home/bin/pRTI cmdline"
    if [[ ! -x "$install4j_launcher" ]]; then
      hla2010_shell_die "install4j launcher not found at $install4j_launcher"
    fi
    install4j_user_home="$(resolve_install4j_user_home "$pitch_user_home")"
    install4j_args=()
    for arg in "${jvm_args[@]}"; do
      install4j_args+=("-J$arg")
    done
    exec env HOME="$install4j_user_home" \
      INSTALL4J_JAVA_HOME_OVERRIDE="${pitch_java_home:-$(cd "$(dirname "$java_bin")/.." && pwd)}" \
      "$install4j_launcher" \
      "${install4j_args[@]}" \
      "$@"
    ;;
  *)
    hla2010_shell_die "unsupported HLA2010_PITCH_LAUNCHER_MODE '$launcher_mode'"
    ;;
esac
