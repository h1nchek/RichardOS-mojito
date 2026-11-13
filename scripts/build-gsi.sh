#!/usr/bin/env bash
set -Eeuo pipefail

RICHARDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_ROOT="${ANDROID_BUILD_TOP:-$(dirname "$RICHARDOS_ROOT")}"
cd "$SOURCE_ROOT"

if [[ ! -f build/envsetup.sh || ! -f device/generic/common/gsi_arm64.mk ]]; then
  echo "ERROR: set ANDROID_BUILD_TOP to a fully synced LineageOS 24.0 source tree." >&2
  exit 2
fi

apply_patch_once() {
  local project="$1"
  local patch="$2"
  if [[ ! -d "$project/.git" || ! -f "$patch" ]]; then
    echo "ERROR: missing source checkout or patch: $project / $patch" >&2
    exit 2
  fi
  if git -C "$project" apply --check "$patch"; then
    git -C "$project" apply "$patch"
    echo "Applied: $patch"
  elif git -C "$project" apply --reverse --check "$patch"; then
    echo "Already applied: $patch"
  else
    echo "ERROR: patch does not apply cleanly: $patch" >&2
    return 1
  fi
  git -C "$project" diff --check
}

# Apply only patches already verified against the LineageOS 24.0 source branch.
apply_patch_once system/netd "$RICHARDOS_ROOT/patches/treble/platform_system_netd/0001-netd-legacy-kernel-oneshot-nonfatal.patch"
apply_patch_once bionic "$RICHARDOS_ROOT/patches/treble/platform_bionic/0001-epoll-pwait2-fallback-legacy-kernels.patch"
apply_patch_once frameworks/av "$RICHARDOS_ROOT/patches/treble/platform_frameworks_av/0001-camera-parameters-null-guard.patch"
apply_patch_once packages/apps/Settings "$RICHARDOS_ROOT/patches/lineage/Settings/0001-settings-add-richardos-dashboard.patch"

export OUT_DIR="${OUT_DIR:-$SOURCE_ROOT/out}"
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
