#!/usr/bin/env bash
set -Eeuo pipefail

# Build the unmodified LineageOS ARM64 GSI baseline.
# This script deliberately applies no RichardOS patches or device-specific files.
RICHARDOS_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_ROOT="${ANDROID_BUILD_TOP:-$(dirname "$RICHARDOS_ROOT")}"
cd "$SOURCE_ROOT"

fail() { echo "ERROR: $*" >&2; exit 2; }

[[ -d .repo ]] || fail "missing .repo directory; use a fully repo-synced Android source tree"
[[ -f build/envsetup.sh ]] || fail "missing build/envsetup.sh"
[[ -f device/generic/common/AndroidProducts.mk ]] || fail "missing generic device product registry"
[[ -f device/generic/common/gsi_arm64.mk ]] || fail "missing generic ARM64 GSI product definition"

grep -Eq '(^|[[:space:]/])gsi_arm64\.mk([[:space:]\\]|$)' device/generic/common/AndroidProducts.mk \
  || fail "AndroidProducts.mk does not register gsi_arm64.mk"

grep -Eq '^PRODUCT_NAME[[:space:]]*:=[[:space:]]*gsi_arm64[[:space:]]*$' device/generic/common/gsi_arm64.mk \
  || fail "unexpected PRODUCT_NAME in upstream GSI product"
grep -Eq '^PRODUCT_DEVICE[[:space:]]*:=[[:space:]]*generic_arm64[[:space:]]*$' device/generic/common/gsi_arm64.mk \
  || fail "unexpected PRODUCT_DEVICE in upstream GSI product"

[[ "$(uname -s)" == Linux && "$(uname -m)" == x86_64 ]] || fail "use a Linux x86_64 build host"

cpu_count="$(nproc)"
mem_kb="$(awk '/MemTotal/ {print $2}' /proc/meminfo)"
mem_gib="$((mem_kb / 1024 / 1024))"
free_gib="$(df -BG . | awk 'NR==2 {gsub(/G/, "", $4); print $4}')"
printf 'Build host: %s | %s vCPU | %s GiB RAM | %s GiB free disk\n' "$(uname -m)" "$cpu_count" "$mem_gib" "$free_gib"
(( cpu_count >= 8 )) || fail "at least 8 vCPU required; 16 recommended"
(( mem_gib >= 28 )) || fail "at least 28 GiB RAM required; 64 GiB recommended"
(( free_gib >= 300 )) || fail "at least 300 GiB free disk required; 500 GiB recommended"

for tool in git python3 java make sha256sum; do
  command -v "$tool" >/dev/null 2>&1 || fail "missing required host tool: $tool"
done

source build/envsetup.sh
# Candidate alias based on the registered product name. Validate resolved
# product variables immediately; stop rather than building a different target.
lunch gsi_arm64-userdebug
[[ "${TARGET_PRODUCT:-}" == "gsi_arm64" ]] || fail "lunch resolved TARGET_PRODUCT='${TARGET_PRODUCT:-unset}', expected gsi_arm64"
[[ "${TARGET_BUILD_VARIANT:-}" == "userdebug" ]] || fail "lunch resolved TARGET_BUILD_VARIANT='${TARGET_BUILD_VARIANT:-unset}', expected userdebug"
[[ "${TARGET_DEVICE:-}" == "generic_arm64" ]] || fail "lunch resolved TARGET_DEVICE='${TARGET_DEVICE:-unset}', expected generic_arm64"

export OUT_DIR="${OUT_DIR:-$SOURCE_ROOT/out}"
jobs="${JOBS:-$cpu_count}"
[[ "$jobs" =~ ^[1-9][0-9]*$ ]] || fail "JOBS must be a positive integer"
(( jobs <= cpu_count )) || fail "JOBS cannot exceed available CPU threads"

echo "Building unmodified LineageOS gsi_arm64 baseline (no RichardOS patches)."
m -j"$jobs" systemimage

IMAGE="$OUT_DIR/target/product/generic_arm64/system.img"
[[ -s "$IMAGE" ]] || fail "build completed without expected image: $IMAGE"

sha256sum "$IMAGE" | tee "$IMAGE.sha256"
repo manifest -r -o "$OUT_DIR/target/product/generic_arm64/resolved-manifest.xml"
printf 'GSI_IMAGE=%s\n' "$IMAGE"
echo "Baseline build complete. No device compatibility or boot test is implied."
