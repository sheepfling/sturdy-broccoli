#!/usr/bin/env bash
set -euo pipefail

timeout_seconds="${HLA2010_PITCH_UI_AUTOMATION_TIMEOUT:-20}"
poll_interval="${HLA2010_PITCH_UI_AUTOMATION_POLL_INTERVAL:-1}"

if ! command -v osascript >/dev/null 2>&1; then
  exit 0
fi

deadline="$((SECONDS + timeout_seconds))"
while [[ "$SECONDS" -lt "$deadline" ]]; do
  if osascript <<'APPLESCRIPT' >/dev/null 2>&1; then
tell application "System Events"
  if exists process "java" then
    tell process "java"
      set frontmost to true
      if exists window 1 then
        try
          click button "Accept" of window 1
          return true
        end try
        try
          keystroke return
          return true
        end try
      end if
    end tell
  end if
end tell
false
APPLESCRIPT
    exit 0
  fi
  sleep "$poll_interval"
done

exit 0
