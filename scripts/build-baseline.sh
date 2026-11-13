#!/usr/bin/env bash
# Build a clean LineageOS baseline for mojito before layering RichardOS branding.
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ANDROID_DIR="${1:-$HOME/android/richardos-mojito}"
DEFAULT_JOBS="$(nproc)"
if (( DEFAULT_JOBS > 8 )); then DEFAULT_JOBS=8; fi
JOBS="${JOBS:-$DEFAULT_JOBS}"

fail() { echo "ERROR: $*" >&2; exit 1; }

[[ "$JOBS" =~ ^[1-9][0-9]*$ ]] && (( JOBS <= 8 )) || fail "JOBS must be an integer from 1 to 8."
[[ "$(uname -s)" == Linux && "$(uname -m)" == x86_64 ]] || fail "Use a Linux x86_64 build host."
command -v repo >/dev/null 2>&1 || fail "Android repo tool is missing from PATH."
command -v python3 >/dev/null 2>&1 || fail "Python 3 is required."
command -v git >/dev/null 2>&1 || fail "git is required."
command -v sha256sum >/dev/null 2>&1 || fail "sha256sum is required."
bash "$ROOT/scripts/check-build-deps.sh"

ANDROID_DIR="$(realpath -m "$ANDROID_DIR")"
[[ -d "$ANDROID_DIR/.repo" ]] || fail "No repo checkout at $ANDROID_DIR. Follow docs/FIRST_BUILD.md to initialize and sync sources first."
[[ -f "$ANDROID_DIR/build/envsetup.sh" ]] || fail "Missing build/envsetup.sh; source sync is incomplete."
[[ -f "$ANDROID_DIR/device/xiaomi/mojito/lineage_mojito.mk" ]] || fail "Missing mojito product makefile."
[[ -f "$ANDROID_DIR/device/xiaomi/sm6150-common/BoardConfigCommon.mk" ]] || fail "Missing SM6150 common device tree."
[[ -f "$ANDROID_DIR/device/qcom/sepolicy/SEPolicy.mk" ]] || fail "Missing Qualcomm QSSI sepolicy tree (device/qcom/sepolicy)."
[[ -f "$ANDROID_DIR/device/qcom/sepolicy_vndr/SEPolicy.mk" ]] || fail "Missing Qualcomm vendor sepolicy tree (device/qcom/sepolicy_vndr)."
[[ -f "$ANDROID_DIR/device/lineage/sepolicy/libion/sepolicy.mk" ]] || fail "Missing LineageOS libion sepolicy integration."
[[ -f "$ANDROID_DIR/device/lineage/sepolicy/libperfmgr/sepolicy.mk" ]] || fail "Missing LineageOS libperfmgr sepolicy integration."
bash "$ROOT/scripts/check-build-host.sh" post-sync "$ANDROID_DIR"

AVAILABLE_GB="$(df -BG "$ANDROID_DIR" | awk 'NR==2 {gsub(/G/,"",$4); print $4}')"
[[ -n "$AVAILABLE_GB" ]] || fail "Could not determine free disk space."
(( AVAILABLE_GB >= 80 )) || fail "At least 80 GB free is recommended for the build phase; found ${AVAILABLE_GB} GB."
MEMORY_KB="$(awk '/MemTotal/ {print $2}' /proc/meminfo)"
MEMORY_GB=$(( MEMORY_KB / 1024 / 1024 ))
(( MEMORY_GB >= 32 )) || fail "At least 32 GB RAM is recommended; found ${MEMORY_GB} GB."

echo "Running manifest and repository tests..."
python3 "$ROOT/scripts/audit_repo_manifests.py" "$ROOT/manifests/mojito-lineage24.xml"
python3 -m unittest discover -s "$ROOT/tests" -v

cd "$ANDROID_DIR"
echo "Checking local manifest extensions against the synced LineageOS manifest..."
python3 "$ROOT/scripts/audit_manifest_dependencies.py" \
  "$ROOT/manifests/mojito-lineage24.xml" \
  "$ANDROID_DIR/.repo/manifests/default.xml" \
  "$ANDROID_DIR/.repo/manifests/snippets/lineage.xml"
REQUIRED_SOURCE_DIRS=(
  device/qcom/sepolicy device/qcom/sepolicy_vndr device/lineage/sepolicy
  hardware/xiaomi hardware/google/interfaces hardware/google/pixel
  hardware/lineage/interfaces hardware/qcom-caf/bootctrl hardware/qcom-caf/common
  hardware/qcom-caf/sm8150/audio hardware/qcom-caf/sm8150/display
  hardware/qcom-caf/sm8150/media hardware/qcom-caf/wlan
  vendor/qcom/opensource/dataservices vendor/qcom/opensource/commonsys-intf/display
  vendor/qcom/opensource/display vendor/qcom/opensource/interfaces vendor/qcom/opensource/usb
)
for relative_path in "${REQUIRED_SOURCE_DIRS[@]}"; do
  [[ -d "$ANDROID_DIR/$relative_path" ]] || fail "Missing required device dependency: $relative_path"
done

echo "Checking the resolved repo manifest..."
repo manifest -r -o "$ANDROID_DIR/resolved-manifest-richardos.xml"

echo "Applying the guarded SM6150 VINTF ordering correction..."
python3 "$ROOT/scripts/patch-mojito-device-tree.py"

echo "Auditing proprietary vendor source paths..."
python3 "$ROOT/scripts/audit-vendor-blobs.py" "$ANDROID_DIR"

echo "Auditing device and Qualcomm VINTF manifests..."
python3 "$ROOT/scripts/audit-vintf.py" \
  device/xiaomi/sm6150-common/configs/manifests/manifest.xml \
  hardware/qcom-caf/sm8150/media/conf_files/sm6150/c2_manifest_vendor.xml

echo
echo "Starting clean LineageOS baseline build for mojito."
echo "No RichardOS branding, wallpaper package, or Settings patch is applied by this script."
source build/envsetup.sh
breakfast mojito
m bacon -j"$JOBS"

OUT_DIR="$ANDROID_DIR/out/target/product/mojito"
[[ -d "$OUT_DIR" ]] || fail "Build returned without the expected product output directory."
mapfile -t PACKAGES < <(find "$OUT_DIR" -maxdepth 1 -type f -name '*.zip' -print | sort)
if (( ${#PACKAGES[@]} == 0 )); then
  echo "Build command completed, but no ZIP package was found in $OUT_DIR." >&2
  exit 1
fi

echo
echo "Baseline build package(s):"
for package in "${PACKAGES[@]}"; do
  sha256sum "$package"
done
echo "Baseline build finished. Do not flash until the package target, checksum, and installation procedure have been independently reviewed."
