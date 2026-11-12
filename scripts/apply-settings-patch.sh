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
TRACKING_REF="refs/remotes/origin/lineage-24.0"

# Android repo checkouts commonly use a detached HEAD. Accept that only when
# the synced commit is an ancestor of the fetched LineageOS target branch.
if git -C "$SETTINGS_DIR" show-ref --verify --quiet "$TRACKING_REF"; then
    if ! git -C "$SETTINGS_DIR" merge-base --is-ancestor HEAD "$TRACKING_REF"; then
        echo "Error: HEAD is not based on origin/lineage-24.0." >&2
        exit 2
    fi
elif [[ "$BRANCH" != "lineage-24.0" ]]; then
    echo "Error: expected lineage-24.0 (or its detached repo-sync checkout); got branch: $BRANCH" >&2
    exit 2
fi

if [[ -n "$(git -C "$SETTINGS_DIR" status --porcelain --untracked-files=all)" ]]; then
    echo "Error: Settings checkout has tracked or untracked local changes; commit or stash them first." >&2
    exit 2
fi

echo "Checking patch applicability..."
git -C "$SETTINGS_DIR" apply --check "$PATCH"

echo "Applying RichardOS Settings dashboard patch..."
git -C "$SETTINGS_DIR" apply "$PATCH"

echo "Patch applied. Review with:"
echo "  git -C \"$SETTINGS_DIR\" diff --check"
echo "  git -C \"$SETTINGS_DIR\" diff"
