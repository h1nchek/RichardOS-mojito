#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ANDROID_DIR="${1:-$HOME/android/richardos-mojito}"
DEFAULT_JOBS="$(nproc)"
if (( DEFAULT_JOBS > 8 )); then DEFAULT_JOBS=8; fi
JOBS="${JOBS:-$DEFAULT_JOBS}"
if [[ ! "$JOBS" =~ ^[1-9][0-9]*$ ]] || (( JOBS > 8 )); then
  echo "ERROR: JOBS must be an integer from 1 to 8; got: $JOBS" >&2
  exit 1
fi
if [[ "$(uname -s)" != Linux || "$(uname -m)" != x86_64 ]]; then
  echo "ERROR: use a Linux x86_64 build host." >&2
  exit 1
fi
command -v repo >/dev/null 2>&1 || { echo "ERROR: Android repo tool is not installed or not in PATH." >&2; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "ERROR: Python 3 is required." >&2; exit 1; }
command -v rsvg-convert >/dev/null 2>&1 || command -v inkscape >/dev/null 2>&1 || {
  echo "ERROR: install librsvg (rsvg-convert) or Inkscape for RichardOS wallpaper assets." >&2
  exit 1
}
python3 "$ROOT/scripts/audit_repo_manifests.py" "$ROOT/manifests/mojito-lineage24.xml"
echo "Running RichardOS helper unit tests..."
python3 -m unittest discover -s "$ROOT/tests" -v
mkdir -p "$ANDROID_DIR"
AVAILABLE_GB="$(df -BG "$ANDROID_DIR" | awk 'NR==2 {gsub(/G/,"",$4); print $4}')"
if [[ -z "$AVAILABLE_GB" || "$AVAILABLE_GB" -lt 350 ]]; then
  echo "ERROR: at least 350 GB free SSD space is recommended; found ${AVAILABLE_GB:-unknown} GB." >&2
  exit 1
fi
cd "$ANDROID_DIR"
repo init -u https://github.com/LineageOS/android.git -b lineage-24.0 --git-lfs --no-clone-bundle
mkdir -p .repo/local_manifests
cp "$ROOT/manifests/mojito-lineage24.xml" .repo/local_manifests/richardos-mojito.xml
echo "Syncing LineageOS and Redmi Note 10 sources..."
repo sync -j"$JOBS" --fail-fast
REQUIRED_SOURCE_DIRS=(
  hardware/xiaomi hardware/google/interfaces hardware/google/pixel
  hardware/lineage/interfaces hardware/qcom-caf/bootctrl hardware/qcom-caf/common
  hardware/qcom-caf/sm8150/audio hardware/qcom-caf/sm8150/display
  hardware/qcom-caf/sm8150/media hardware/qcom-caf/wlan
  vendor/qcom/opensource/dataservices vendor/qcom/opensource/commonsys-intf/display
  vendor/qcom/opensource/display vendor/qcom/opensource/interfaces vendor/qcom/opensource/usb
)
for relative_path in "${REQUIRED_SOURCE_DIRS[@]}"; do
  [[ -d "$ANDROID_DIR/$relative_path" ]] || { echo "ERROR: missing source project: $relative_path" >&2; exit 1; }
done
echo "Checking proprietary vendor source paths..."
python3 "$ROOT/scripts/audit-vendor-blobs.py" "$ANDROID_DIR"
echo "Applying guarded SM6150 VINTF ordering correction..."
python3 "$ROOT/scripts/patch-mojito-device-tree.py"
echo "Installing RichardOS system identity, gold palette, and boot animation..."
bash "$ROOT/scripts/install-system-branding.sh" "$ANDROID_DIR"
echo "Installing RichardOS wallpaper resources into the synced source tree..."
bash "$ROOT/scripts/install-wallpaper-picker.sh" "$ANDROID_DIR"
bash "$ROOT/scripts/install-wallpaper-overlay.sh" "$ANDROID_DIR" device/xiaomi/mojito/lineage_mojito.mk
echo "Checking device and Qualcomm VINTF XML..."
python3 "$ROOT/scripts/audit-vintf.py" \
  device/xiaomi/sm6150-common/configs/manifests/manifest.xml \
  hardware/qcom-caf/sm8150/media/conf_files/sm6150/c2_manifest_vendor.xml
repo manifest -r -o "$ROOT/resolved-manifest-richardos.xml"
source build/envsetup.sh
breakfast mojito
m bacon -j"$JOBS"
echo "RichardOS build completed. Inspect the output, verify ZIP and SHA-256, then arrange physical-device testing."
