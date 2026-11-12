#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PATCH="$ROOT/patches/lineage/Settings/0001-settings-add-richardos-dashboard.patch"
SETTINGS_DIR="${1:-}"

if [[ -z "$SETTINGS_DIR" ]]; then
    echo "Usage: $0 /path/to/lineage/packages/apps/Settings" >&2
    exit 2
fi

if [[ ! -d "$SETTINGS_DIR/.git" ]]; then
    echo "Error: not a Git checkout: $SETTINGS_DIR" >&2
    exit 2
fi

REMOTE="$(git -C "$SETTINGS_DIR" remote get-url origin 2>/dev/null || true)"
case "$REMOTE" in
    *LineageOS/android_packages_apps_Settings*|*LineageOS/android_packages_apps_Settings.git) ;;
    *)
        echo "Error: expected LineageOS/android_packages_apps_Settings, got: $REMOTE" >&2
        exit 2
        ;;
esac

BRANCH="$(git -C "$SETTINGS_DIR" branch --show-current)"
if [[ "$BRANCH" != "lineage-24.0" ]]; then
    echo "Error: expected branch lineage-24.0, got: $BRANCH" >&2
    exit 2
fi

if ! git -C "$SETTINGS_DIR" diff --quiet || ! git -C "$SETTINGS_DIR" diff --cached --quiet; then
    echo "Error: Settings checkout has local modifications; commit or stash them first." >&2
    exit 2
fi

echo "Checking patch applicability..."
git -C "$SETTINGS_DIR" apply --check "$PATCH"

echo "Applying RichardOS Settings dashboard patch..."
git -C "$SETTINGS_DIR" apply "$PATCH"

echo "Patch applied. Review with:"
echo "  git -C \"$SETTINGS_DIR\" diff --check"
echo "  git -C \"$SETTINGS_DIR\" diff"
