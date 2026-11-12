#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_DIR="$ROOT/vendor/richardos/branding/wallpapers"
OUTPUT_DIR="${1:-$ROOT/out/richardos-wallpapers}"
mkdir -p "$OUTPUT_DIR"

if command -v rsvg-convert >/dev/null 2>&1; then
    RENDERER="rsvg"
elif command -v inkscape >/dev/null 2>&1; then
    RENDERER="inkscape"
else
    echo "Missing renderer: install librsvg (rsvg-convert) or Inkscape." >&2
    exit 1
fi

for source in "$SOURCE_DIR"/*.svg; do
    name="$(basename "$source" .svg)"
    output="$OUTPUT_DIR/$name.png"
    case "$RENDERER" in
        rsvg)
            rsvg-convert --width 1440 --height 3200 --format png --output "$output" "$source"
            ;;
        inkscape)
            inkscape "$source" --export-type=png --export-filename="$output" --export-width=1440 --export-height=3200
            ;;
    esac
    file "$output"
done

echo "Rendered wallpaper PNGs to: $OUTPUT_DIR"
echo "Review them on-device before adding them to the default wallpaper overlay."
