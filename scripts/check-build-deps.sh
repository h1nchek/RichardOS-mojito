#!/usr/bin/env bash
# Read-only Ubuntu/Debian package and tool preflight for LineageOS 24 / RichardOS.
set -Eeuo pipefail

fail() { echo "ERROR: $*" >&2; exit 1; }
command -v dpkg-query >/dev/null 2>&1 || fail "This dependency checker supports Ubuntu/Debian systems with dpkg-query."
command -v apt-get >/dev/null 2>&1 || fail "apt-get was not found; install dependencies using your distribution's package manager and re-run."

required_packages=(
  bc bison build-essential ccache curl erofs-utils flex g++-multilib gcc-multilib
  git git-lfs gnupg gperf imagemagick kmod protobuf-compiler python3-protobuf
  lib32readline-dev lib32z1-dev libdw-dev libelf-dev libgnutls28-dev lz4
  libsdl1.2-dev libssl-dev libxml2-utils lzop pngcrush rsync schedtool
  squashfs-tools xsltproc xxd zip zlib1g-dev
)

# LineageOS documents libxml2 for current Ubuntu releases, with libxml2-16
# replacing it on Ubuntu 26.04 and newer.
ubuntu_version=""
if [[ -r /etc/os-release ]]; then
  . /etc/os-release
  [[ "${ID:-}" == ubuntu ]] && ubuntu_version="${VERSION_ID:-}"
fi
if [[ "$ubuntu_version" =~ ^[0-9]+\.[0-9]+$ ]] && awk -v v="$ubuntu_version" 'BEGIN { exit !(v >= 26.04) }'; then
  required_packages+=(libxml2-16)
else
  required_packages+=(libxml2)
fi

missing=()
for package in "${required_packages[@]}"; do
  status="$(dpkg-query -W -f='${db:Status-Status}' "$package" 2>/dev/null || true)"
  [[ "$status" == installed ]] || missing+=("$package")
done

missing_tools=()
for tool in repo python3 git sha256sum; do
  command -v "$tool" >/dev/null 2>&1 || missing_tools+=("$tool")
done
if ! command -v rsvg-convert >/dev/null 2>&1 && ! command -v inkscape >/dev/null 2>&1; then
  missing_tools+=("rsvg-convert (package: librsvg2-bin) or inkscape")
  missing+=(librsvg2-bin)
fi

if (( ${#missing[@]} || ${#missing_tools[@]} )); then
  echo "Build environment is missing prerequisites."
  if (( ${#missing[@]} )); then
    echo "Missing Debian/Ubuntu packages:"
    printf '  %s\n' "${missing[@]}"
    printf '\nSuggested install command (review before running):\nsudo apt-get install %s\n' "${missing[*]}"
  fi
  if (( ${#missing_tools[@]} )); then
    echo "Missing commands/tools:"
    printf '  %s\n' "${missing_tools[@]}"
    echo "The Android repo launcher must be installed separately and available in PATH."
  fi
  exit 1
fi

echo "PASS: documented LineageOS build packages and RichardOS helper tools are present."
echo "This check is read-only; it does not install or change anything."
