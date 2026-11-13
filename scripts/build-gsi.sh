#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ ! -f build/envsetup.sh || ! -f device/generic/common/gsi_arm64.mk ]]; then
  echo "ERROR: run this script from a fully synced LineageOS 24.0 source tree with RichardOS files overlaid." >&2
  exit 2
fi

if [[ -z "${OUT_DIR:-}" ]]; then
  export OUT_DIR="$ROOT/out"
fi

source build/envsetup.sh
lunch gsi_arm64-userdebug
m systemimage

IMAGE="$OUT_DIR/target/product/generic_arm64/system.img"
if [[ ! -s "$IMAGE" ]]; then
  echo "ERROR: build completed without the expected GSI image: $IMAGE" >&2
  exit 3
fi

sha256sum "$IMAGE" | tee "$IMAGE.sha256"
printf 'GSI_IMAGE=%s\n' "$IMAGE"
