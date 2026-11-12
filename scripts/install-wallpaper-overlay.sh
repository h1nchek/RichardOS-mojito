#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ANDROID_TOP="${1:-}"
PRODUCT_MK="${2:-}"

if [[ -z "$ANDROID_TOP" || -z "$PRODUCT_MK" ]]; then
    echo "Usage: $0 /path/to/android/source device/xiaomi/mojito/lineage_mojito.mk" >&2
    exit 2
fi

ANDROID_TOP="$(realpath "$ANDROID_TOP")"
PRODUCT_MK="$ANDROID_TOP/$PRODUCT_MK"
if [[ ! -f "$PRODUCT_MK" ]]; then
    echo "Product makefile not found: $PRODUCT_MK" >&2
    exit 1
fi
if ! grep -q 'PRODUCT_NAME := lineage_mojito' "$PRODUCT_MK"; then
    echo "Refusing to edit: this does not look like the expected mojito product makefile." >&2
    exit 1
fi

SOURCE="$ROOT/vendor/richardos/branding/wallpapers/richardos-nocturne.svg"
OVERLAY="$ANDROID_TOP/vendor/richardos/overlay/frameworks/base/core/res/res/drawable-nodpi"
DEST="$OVERLAY/default_wallpaper.png"

if [[ ! -f "$SOURCE" ]]; then
    echo "Missing wallpaper source: $SOURCE" >&2
    exit 1
fi
if ! command -v rsvg-convert >/dev/null 2>&1 && ! command -v inkscape >/dev/null 2>&1; then
    echo "Install librsvg (rsvg-convert) or Inkscape to render the wallpaper." >&2
    exit 1
fi

mkdir -p "$OVERLAY"
TMP="$DEST.tmp"
if command -v rsvg-convert >/dev/null 2>&1; then
    rsvg-convert --width 1440 --height 3200 --format png --output "$TMP" "$SOURCE"
elif command -v inkscape >/dev/null 2>&1; then
    inkscape "$SOURCE" --export-type=png --export-filename="$TMP" --export-width=1440 --export-height=3200 >/dev/null
else
    echo "Install librsvg (rsvg-convert) or Inkscape to render the wallpaper." >&2
    exit 1
fi
mv "$TMP" "$DEST"

if ! grep -qF 'PRODUCT_PACKAGE_OVERLAYS += vendor/richardos/overlay' "$PRODUCT_MK"; then
    printf '\n# RichardOS resource overlays\nPRODUCT_PACKAGE_OVERLAYS += vendor/richardos/overlay\n' >> "$PRODUCT_MK"
fi

echo "Installed RichardOS default wallpaper overlay:"
echo "  $DEST"
echo "Registered overlay in:"
echo "  $PRODUCT_MK"
echo "Review the image and build framework-res before flashing anything."
