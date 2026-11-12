#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ANDROID_TOP="${1:-}"
PRODUCT_REL="${2:-device/xiaomi/mojito/lineage_mojito.mk}"

if [[ -z "$ANDROID_TOP" ]]; then
    echo "Usage: $0 /path/to/android/source [device/xiaomi/mojito/lineage_mojito.mk]" >&2
    exit 2
fi
ANDROID_TOP="$(realpath "$ANDROID_TOP")"
PRODUCT_MK="$ANDROID_TOP/$PRODUCT_REL"
SOURCE_APP="$ROOT/vendor/richardos/wallpapers"
DEST_APP="$ANDROID_TOP/vendor/richardos/wallpapers"

if [[ ! -f "$PRODUCT_MK" ]] || ! grep -q 'PRODUCT_NAME := lineage_mojito' "$PRODUCT_MK"; then
    echo "Refusing to edit: expected the mojito lineage_mojito product makefile at $PRODUCT_MK" >&2
    exit 1
fi
if ! command -v rsvg-convert >/dev/null 2>&1 && ! command -v inkscape >/dev/null 2>&1; then
    echo "Install librsvg (rsvg-convert) or Inkscape before running this helper." >&2
    exit 1
fi

mkdir -p "$(dirname "$DEST_APP")"
if [[ -e "$DEST_APP" ]]; then
    if ! grep -q 'package="com.richardos.wallpapers"' "$DEST_APP/AndroidManifest.xml" 2>/dev/null ||
       ! grep -q 'name: "RichardOSWallpapers"' "$DEST_APP/Android.bp" 2>/dev/null; then
        echo "Destination exists but is not the expected RichardOS module: $DEST_APP" >&2
        exit 1
    fi
    echo "Updating generated wallpaper resources in existing RichardOS module."
else
    cp -a "$SOURCE_APP" "$DEST_APP"
fi
mkdir -p "$DEST_APP/res/drawable-nodpi"

render() {
    local resource_name="$1"
    local artwork_name="$2"
    local source="$ROOT/vendor/richardos/branding/wallpapers/$artwork_name.svg"
    local full="$DEST_APP/res/drawable-nodpi/$resource_name.png"
    local thumb="$DEST_APP/res/drawable-nodpi/${resource_name}_small.png"
    if command -v rsvg-convert >/dev/null 2>&1; then
        rsvg-convert --width 1440 --height 3200 --format png --output "$full" "$source"
        rsvg-convert --width 360 --height 800 --format png --output "$thumb" "$source"
    else
        inkscape "$source" --export-type=png --export-filename="$full" --export-width=1440 --export-height=3200 >/dev/null
        inkscape "$source" --export-type=png --export-filename="$thumb" --export-width=360 --export-height=800 >/dev/null
    fi
    file "$full" "$thumb"
}
render richardos_nocturne richardos-nocturne
render richardos_eclipse richardos-eclipse
render richardos_aurum richardos-aurum

if ! grep -qF '# RichardOS WallpaperPicker2 partner package' "$PRODUCT_MK"; then
    cat >> "$PRODUCT_MK" <<'EOF'

# RichardOS WallpaperPicker2 partner package
PRODUCT_PACKAGES += RichardOSWallpapers
EOF
fi

echo "Installed RichardOS WallpaperPicker2 partner package at:"
echo "  $DEST_APP"
echo "Registered RichardOSWallpapers in:"
echo "  $PRODUCT_MK"
echo "Next: build the RichardOSWallpapers module and verify discovery in WallpaperPicker2."
