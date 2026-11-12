#!/usr/bin/env bash
# Read-only resource preflight for the RichardOS Android build host.
set -Eeuo pipefail

STAGE="${1:-pre-sync}"
CHECK_PATH="${2:-.}"
case "$STAGE" in
  pre-sync) MIN_FREE_GB=350 ;;
  post-sync) MIN_FREE_GB=80 ;;
  *) echo "Usage: $0 pre-sync|post-sync [path-on-build-filesystem]" >&2; exit 2 ;;
esac

[[ "$(uname -s)" == Linux ]] || { echo "ERROR: Android builds require Linux." >&2; exit 1; }
[[ "$(uname -m)" == x86_64 ]] || { echo "ERROR: this build setup requires x86_64." >&2; exit 1; }
command -v nproc >/dev/null 2>&1 || { echo "ERROR: nproc is required." >&2; exit 1; }
command -v df >/dev/null 2>&1 || { echo "ERROR: df is required." >&2; exit 1; }

CPUS="$(nproc)"
MEMORY_KB="$(awk '/MemTotal/ {print $2}' /proc/meminfo)"
MEMORY_GB=$(( MEMORY_KB / 1024 / 1024 ))
AVAILABLE_BYTES="$(df -B1 --output=avail "$CHECK_PATH" | tail -n 1 | tr -d ' ')"
MIN_FREE_BYTES=$(( MIN_FREE_GB * 1024 * 1024 * 1024 ))

printf 'RichardOS build host preflight (%s)\n' "$STAGE"
printf 'CPU threads: %s (minimum 8)\n' "$CPUS"
printf 'RAM: %s GiB (minimum 32 GiB)\n' "$MEMORY_GB"
printf 'Free disk: %s GiB (minimum %s GiB)\n' \
  "$(( AVAILABLE_BYTES / 1024 / 1024 / 1024 ))" "$MIN_FREE_GB"

(( CPUS >= 8 )) || { echo "ERROR: at least 8 CPU threads are required for this build plan." >&2; exit 1; }
(( MEMORY_GB >= 32 )) || { echo "ERROR: at least 32 GiB RAM is required for this build plan." >&2; exit 1; }
(( AVAILABLE_BYTES >= MIN_FREE_BYTES )) || {
  echo "ERROR: insufficient free space on $CHECK_PATH." >&2
  exit 1
}

echo "PASS: build host meets the selected stage requirements."
