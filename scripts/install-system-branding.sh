#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ANDROID_TOP="${1:-}"
PRODUCT_REL="${2:-device/xiaomi/mojito/lineage_mojito.mk}"
[[ -n "$ANDROID_TOP" ]] || { echo "Usage: $0 /path/to/android/source [product.mk]" >&2; exit 2; }
ANDROID_TOP="$(realpath "$ANDROID_TOP")"
PRODUCT_MK="$ANDROID_TOP/$PRODUCT_REL"
DEST="$ANDROID_TOP/vendor/richardos/bootanimation"
LOGO="$ROOT/vendor/richardos/branding/richardos-lion.svg"

[[ -f "$PRODUCT_MK" ]] || { echo "Missing product makefile: $PRODUCT_MK" >&2; exit 1; }
grep -q 'PRODUCT_NAME := lineage_mojito' "$PRODUCT_MK" || { echo "Not the expected mojito product makefile." >&2; exit 1; }
command -v python3 >/dev/null
command -v rsvg-convert >/dev/null || command -v inkscape >/dev/null || { echo "Install librsvg (rsvg-convert) or Inkscape."; exit 1; }
command -v zip >/dev/null || { echo "zip is required."; exit 1; }

mkdir -p "$DEST/part0"
mkdir -p "$ANDROID_TOP/vendor/richardos/overlay"
cp -a "$ROOT/vendor/richardos/overlay/." "$ANDROID_TOP/vendor/richardos/overlay/"
python3 - "$LOGO" "$DEST/frames" <<'PY'
import math, pathlib, sys, xml.etree.ElementTree as ET
source, output = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
root = ET.parse(source).getroot()
path = root.find("{http://www.w3.org/2000/svg}path")
if path is None:
    raise SystemExit("Lion SVG has no path element")
d = path.attrib["d"]
output.mkdir(parents=True, exist_ok=True)
for frame in range(24):
    phase = frame / 24 * math.tau
    scale = 1.48 + 0.025 * math.sin(phase)
    opacity = 0.76 + 0.20 * (0.5 + 0.5 * math.sin(phase))
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="2400" viewBox="0 0 1080 2400">
<defs><radialGradient id="bg"><stop offset="0" stop-color="#202329"/><stop offset="1" stop-color="#090A0D"/></radialGradient></defs>
<rect width="1080" height="2400" fill="url(#bg)"/>
<path d="{d}" fill="#F5BE35" opacity="{opacity:.4f}" transform="translate(540 1200) scale({scale:.5f}) translate(-256 -256)"/>
</svg>'''
    (output / f"{frame:05d}.svg").write_text(svg)
PY

rm -f "$DEST/part0/"*.png
for svg in "$DEST/frames/"*.svg; do
    name="$(basename "$svg" .svg)"
    if command -v rsvg-convert >/dev/null 2>&1; then
        rsvg-convert --width 1080 --height 2400 --output "$DEST/part0/$name.png" "$svg"
    else
        inkscape "$svg" --export-type=png --export-filename="$DEST/part0/$name.png" --export-width=1080 --export-height=2400 >/dev/null
    fi
done
printf '1080 2400 30\np 0 0 part0\n' > "$DEST/desc.txt"
(
  cd "$DEST"
  rm -f bootanimation.zip
  zip -q -0 -r bootanimation.zip desc.txt part0
)
mkdir -p "$ANDROID_TOP/vendor/richardos"
cp "$DEST/bootanimation.zip" "$ANDROID_TOP/vendor/richardos/bootanimation.zip"

if ! grep -qF '# RichardOS product branding' "$PRODUCT_MK"; then
    cat >> "$PRODUCT_MK" <<'EOF'

# RichardOS product branding
$(call inherit-product, vendor/richardos/config/branding.mk)
PRODUCT_COPY_FILES += vendor/richardos/bootanimation.zip:system/media/bootanimation.zip
EOF
fi
# Make RichardOS overlays visible to the Android resource merger.
if ! grep -qF '# RichardOS resource overlays' "$PRODUCT_MK"; then
    cat >> "$PRODUCT_MK" <<'EOF'

# RichardOS resource overlays
PRODUCT_PACKAGE_OVERLAYS += vendor/richardos/overlay
EOF
fi

echo "Generated RichardOS bootanimation and registered product branding."
