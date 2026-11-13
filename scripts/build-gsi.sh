#!/usr/bin/env bash
set -Eeuo pipefail

# Run on a dedicated Linux build host with a fully synced LineageOS tree.
RICHARDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_ROOT="${ANDROID_BUILD_TOP:-$(dirname "$RICHARDOS_ROOT")}"
cd "$SOURCE_ROOT"

fail() { echo "ERROR: $*" >&2; exit 2; }

[[ -f build/envsetup.sh ]] || fail "missing build/envsetup.sh; sync the LineageOS source tree first"
[[ -f device/generic/common/gsi_arm64.mk ]] || fail "missing generic ARM64 GSI product definition"
[[ -d .repo ]] || fail "missing .repo directory; this must be a repo-synced Android source tree"

arch="$(uname -m)"
[[ "$arch" == "x86_64" ]] || fail "Android host build requires x86_64; detected $arch"

cpu_count="$(nproc)"
mem_kb="$(awk '/MemTotal/ {print $2}' /proc/meminfo)"
mem_gib="$((mem_kb / 1024 / 1024))"
free_gib="$(df -BG . | awk 'NR==2 {gsub(/G/, "", $4); print $4}')"

printf 'Build host: %s | %s vCPU | %s GiB RAM | %s GiB free disk\n' "$arch" "$cpu_count" "$mem_gib" "$free_gib"
(( cpu_count >= 8 )) || fail "at least 8 vCPU are required; 16 recommended"
(( mem_gib >= 28 )) || fail "at least 28 GiB RAM required; 64 GiB recommended"
(( free_gib >= 300 )) || fail "at least 300 GiB free disk required; use a 500 GiB NVMe volume"

for tool in git python3 java clang lz4; do
  command -v "$tool" >/dev/null 2>&1 || fail "missing required host tool: $tool"
done

apply_patch_once() {
  local project="$1"
  local patch="$2"
  [[ -d "$project/.git" && -f "$patch" ]] || fail "missing source checkout or patch: $project / $patch"
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

# Only patches that passed source-branch applicability checks are included.
apply_patch_once system/netd "$RICHARDOS_ROOT/patches/treble/platform_system_netd/0001-netd-legacy-kernel-oneshot-nonfatal.patch"
apply_patch_once bionic "$RICHARDOS_ROOT/patches/treble/platform_bionic/0001-epoll-pwait2-fallback-legacy-kernels.patch"
apply_patch_once frameworks/av "$RICHARDOS_ROOT/patches/treble/platform_frameworks_av/0001-camera-parameters-null-guard.patch"
apply_patch_once packages/apps/Settings "$RICHARDOS_ROOT/patches/lineage/Settings/0001-settings-add-richardos-dashboard.patch"

export OUT_DIR="${OUT_DIR:-$SOURCE_ROOT/out}"
source build/envsetup.sh
lunch gsi_arm64-userdebug
m -j"$cpu_count" systemimage

IMAGE="$OUT_DIR/target/product/generic_arm64/system.img"
[[ -s "$IMAGE" ]] || fail "build ended without expected image: $IMAGE"
sha256sum "$IMAGE" | tee "$IMAGE.sha256"
printf 'GSI_IMAGE=%s\n' "$IMAGE"
