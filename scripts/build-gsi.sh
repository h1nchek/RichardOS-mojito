#!/usr/bin/env bash
set -Eeuo pipefail

# Build the generic ARM64 GSI in two deliberately separate stages:
#   baseline  - untouched upstream LineageOS GSI (default, first build)
#   richardos - apply reviewed RichardOS compatibility + Settings patches
RICHARDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_ROOT="${ANDROID_BUILD_TOP:-$(dirname "$RICHARDOS_ROOT")}"
MODE="${RICHARDOS_GSI_MODE:-baseline}"
cd "$SOURCE_ROOT"

fail() { echo "ERROR: $*" >&2; exit 2; }

case "$MODE" in
  baseline|richardos) ;;
  *) fail "RICHARDOS_GSI_MODE must be 'baseline' or 'richardos' (got: $MODE)" ;;
esac

[[ -f build/envsetup.sh ]] || fail "missing build/envsetup.sh; sync the LineageOS source tree first"
[[ -f device/generic/common/gsi_arm64.mk ]] || fail "missing generic ARM64 GSI product definition"
[[ -d .repo ]] || fail "missing .repo directory; this must be a repo-synced Android source tree"

arch="$(uname -m)"
[[ "$arch" == "x86_64" ]] || fail "Android host build requires x86_64; detected $arch"

cpu_count="$(nproc)"
mem_kb="$(awk '/MemTotal/ {print $2}' /proc/meminfo)"
mem_gib="$((mem_kb / 1024 / 1024))"
free_gib="$(df -BG . | awk 'NR==2 {gsub(/G/, "", $4); print $4}')"

printf 'RichardOS GSI mode: %s\n' "$MODE"
printf 'Build host: %s | %s vCPU | %s GiB RAM | %s GiB free disk\n' "$arch" "$cpu_count" "$mem_gib" "$free_gib"
(( cpu_count >= 8 )) || fail "at least 8 vCPU are required; 16 recommended"
(( mem_gib >= 28 )) || fail "at least 28 GiB RAM required; 64 GiB recommended"
(( free_gib >= 300 )) || fail "at least 300 GiB free disk required; use a 500 GiB NVMe volume"

for tool in git python3 java make repo sha256sum date; do
  command -v "$tool" >/dev/null 2>&1 || fail "missing required host tool: $tool"
done

export OUT_DIR="${OUT_DIR:-$SOURCE_ROOT/out}"
mkdir -p "$OUT_DIR"

# Record exact project revisions; lineage-24.0 is a moving branch.
repo manifest -r -o "$OUT_DIR/manifest.lock.xml"
[[ -s "$OUT_DIR/manifest.lock.xml" ]] || fail "repo did not produce a pinned manifest snapshot"
manifest_sha256="$(sha256sum "$OUT_DIR/manifest.lock.xml" | awk '{print $1}')"

apply_patch_once() {
  local project="$1"
  local patch="$2"
  git -C "$project" rev-parse --git-dir >/dev/null 2>&1 || fail "missing Git checkout: $project"
  [[ -f "$patch" ]] || fail "missing patch file: $patch"
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

if [[ "$MODE" == "richardos" ]]; then
  # Integration is opt-in and happens only after the upstream baseline is built.
  apply_patch_once system/netd "$RICHARDOS_ROOT/patches/treble/platform_system_netd/0001-netd-legacy-kernel-oneshot-nonfatal.patch"
  apply_patch_once bionic "$RICHARDOS_ROOT/patches/treble/platform_bionic/0001-epoll-pwait2-fallback-legacy-kernels.patch"
  apply_patch_once frameworks/av "$RICHARDOS_ROOT/patches/treble/platform_frameworks_av/0001-camera-parameters-null-guard.patch"
  apply_patch_once packages/apps/Settings "$RICHARDOS_ROOT/patches/lineage/Settings/0001-settings-add-richardos-dashboard.patch"
else
  echo "Baseline mode: no RichardOS patches will be applied."
fi

source build/envsetup.sh
lunch gsi_arm64-userdebug

actual_product="$(get_build_var TARGET_PRODUCT)"
actual_device="$(get_build_var TARGET_DEVICE)"
actual_variant="$(get_build_var TARGET_BUILD_VARIANT)"
[[ "$actual_product" == "gsi_arm64" ]] || fail "unexpected TARGET_PRODUCT: $actual_product"
[[ "$actual_device" == "generic_arm64" ]] || fail "unexpected TARGET_DEVICE: $actual_device"
[[ "$actual_variant" == "userdebug" ]] || fail "unexpected TARGET_BUILD_VARIANT: $actual_variant"

m -j"$cpu_count" systemimage

IMAGE="$OUT_DIR/target/product/generic_arm64/system.img"
[[ -s "$IMAGE" ]] || fail "build ended without expected image: $IMAGE"
image_sha256="$(sha256sum "$IMAGE" | tee "$IMAGE.sha256" | awk '{print $1}')"
{
  printf 'RICHARDOS_VERSION=0.9.0-pre-release\n'
  printf 'GSI_MODE=%s\n' "$MODE"
  printf 'BUILD_UTC=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  printf 'SOURCE_ROOT=%s\n' "$SOURCE_ROOT"
  printf 'MANIFEST_SHA256=%s\n' "$manifest_sha256"
  printf 'IMAGE_SHA256=%s\n' "$image_sha256"
  printf 'TARGET_PRODUCT=%s\n' "$actual_product"
  printf 'TARGET_DEVICE=%s\n' "$actual_device"
  printf 'TARGET_BUILD_VARIANT=%s\n' "$actual_variant"
} | tee "$OUT_DIR/richardos-build-info.txt"
printf 'GSI_MODE=%s\nGSI_IMAGE=%s\n' "$MODE" "$IMAGE"
