#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# shellcheck source=lib/shell.sh
source "$ROOT_DIR/scripts/lib/shell.sh"
hla2010_shell_init "$0"

usage() {
  cat <<'EOF'
usage: ./bootstrap [python|certi|pitch|all|doctor]

Profiles:
  python  bootstrap the editable Python package and lean test dependencies
  certi   bootstrap python, then build the repo-local CERTI runtime
  pitch   bootstrap python, then build the Pitch Docker image
  all     bootstrap python, CERTI, and Pitch
  doctor  check Python, .venv, imports, and optional backend prerequisites

Override the Python extras with HLA2010_BOOTSTRAP_EXTRAS when needed.
The default profile uses the lightweight "test" extras unless overridden.
EOF
}

bootstrap_python_profile() {
  local extras="${HLA2010_BOOTSTRAP_EXTRAS:-test}"
  hla2010_shell_log "bootstrap python extras=${extras}"
  HLA2010_BOOTSTRAP_EXTRAS="$extras" "$ROOT_DIR/scripts/bootstrap_python.sh"
}

bootstrap_certi_profile() {
  hla2010_shell_log "bootstrap certi"
  "$ROOT_DIR/scripts/rebuild_certi.sh"
}

bootstrap_pitch_profile() {
  hla2010_shell_log "bootstrap pitch"
  "$ROOT_DIR/scripts/pitch_docker_easy.sh" install
}

case "${1:-python}" in
  python)
    bootstrap_python_profile
    ;;
  certi)
    bootstrap_python_profile
    bootstrap_certi_profile
    ;;
  pitch)
    bootstrap_python_profile
    bootstrap_pitch_profile
    ;;
  all)
    bootstrap_python_profile
    bootstrap_certi_profile
    bootstrap_pitch_profile
    ;;
  doctor)
    hla2010_shell_log "bootstrap doctor"
    trap - ERR
    set +e
    "$ROOT_DIR/scripts/doctor.py" "${@:2}"
    doctor_status=$?
    exit "$doctor_status"
    ;;
  help|-h|--help)
    usage
    ;;
  *)
    usage >&2
    exit 2
    ;;
esac
