#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
pitch_home="${HLA2010_PITCH_HOME:-}"

if [[ -z "$pitch_home" && -d "$ROOT_DIR/third_party/pitch/PITCH-prti1516e-manual" ]]; then
  pitch_home="$ROOT_DIR/third_party/pitch/PITCH-prti1516e-manual"
fi
if [[ -z "$pitch_home" && -d "$ROOT_DIR/../hla-python/INBOX/PITCH-prti1516e-manual" ]]; then
  pitch_home="$ROOT_DIR/../hla-python/INBOX/PITCH-prti1516e-manual"
fi
if [[ -z "$pitch_home" ]]; then
  echo "error: Pitch runtime home not found; set HLA2010_PITCH_HOME"
  exit 1
fi

pitch_user_home="$pitch_home/user.home"
java_bin="$pitch_home/Contents/Home/bin/java"
java_library_path="$pitch_home/lib:$pitch_home/.i4j_external_12081/lib:$pitch_home/.i4j_external_12081/lib/clang12"
prti_jar="$pitch_home/lib/prtifull.jar"

mkdir -p "$pitch_user_home/.cache"

if [[ $# -eq 0 ]]; then
  set -- -nogui -verbose
fi

exec env HOME="$pitch_user_home" \
  "$java_bin" \
  -Xmx512m \
  -Duser.home="$pitch_user_home" \
  -Djava.library.path="$java_library_path" \
  -jar "$prti_jar" \
  -nocmdline \
  "$@"
