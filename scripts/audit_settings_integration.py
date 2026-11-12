#!/usr/bin/env python3
"""Check RichardOS Settings Java references against pinned Android/Lineage sources."""

from __future__ import annotations

import argparse
import pathlib
import re
import sys


def require(source: str, pattern: str, label: str, failures: list[str]) -> None:
    if not re.search(pattern, source, re.MULTILINE | re.DOTALL):
        failures.append(f"missing upstream API: {label}")


def read(path: pathlib.Path, failures: list[str]) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as error:
        failures.append(f"cannot read {path}: {error}")
        return ""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("settings_root", type=pathlib.Path)
    parser.add_argument("frameworks_base_root", type=pathlib.Path)
    parser.add_argument("settings_patch", type=pathlib.Path)
    args = parser.parse_args()

    settings = args.settings_root
    base = args.frameworks_base_root
    failures: list[str] = []

    secure_settings = read(
        base / "core/java/android/provider/Settings.java", failures
    )
    storage = read(
        base / "core/java/android/os/storage/StorageManager.java", failures
    )
    selinux = read(base / "core/java/android/os/SELinux.java", failures)
    properties = read(base / "core/java/android/os/SystemProperties.java", failures)

    system_dashboard = read(
        settings / "src/com/android/settings/system/SystemDashboardFragment.java",
        failures,
    )
    require(
        system_dashboard,
        r"SettingsEnums\.SETTINGS_SYSTEM_CATEGORY",
        "SettingsEnums.SETTINGS_SYSTEM_CATEGORY used by upstream Settings",
        failures,
    )
    require(
        secure_settings,
        r"THEME_CUSTOMIZATION_OVERLAY_PACKAGES",
        "Settings.Secure.THEME_CUSTOMIZATION_OVERLAY_PACKAGES",
        failures,
    )
    require(
        storage,
        r"public\s+static\s+boolean\s+isEncrypted\s*\(\s*\)",
        "StorageManager.isEncrypted()",
        failures,
    )
    require(
        selinux,
        r"isSELinuxEnabled\s*\(",
        "SELinux.isSELinuxEnabled()",
        failures,
    )
    require(
        selinux,
        r"isSELinuxEnforced\s*\(",
        "SELinux.isSELinuxEnforced()",
        failures,
    )
    require(
        properties,
        r"get\s*\(\s*String\s+key\s*,\s*String\s+def\s*\)",
        "SystemProperties.get(String, String)",
        failures,
    )

    lock_screen = settings / (
        "src/com/android/settings/notification/"
        "LockScreenNotificationsPreferencePageFragment.java"
    )
    if not lock_screen.is_file():
        failures.append("missing upstream LockScreenNotificationsPreferencePageFragment")

    gateway = ""
    patch_path = args.settings_patch
    patch = read(patch_path, failures)
    target = "src/com/android/settings/core/gateway/SettingsGateway.java"
    current = None
    added: list[str] = []
    for line in patch.splitlines():
        if line.startswith("+++ b/"):
            current = line[6:]
        elif line.startswith("diff --git "):
            current = None
        elif current == target and line.startswith("+") and not line.startswith("+++"):
            added.append(line[1:])
    gateway = "\n".join(added)
    for fragment in (
        "RichardOSDashboardFragment",
        "RichardOSStatusBarFragment",
        "RichardOSRootFragment",
    ):
        if f"com.android.settings.richardos.{fragment}" not in gateway:
            failures.append(f"SettingsGateway does not register {fragment}")

    if failures:
        for failure in failures:
            print(f"error: {failure}", file=sys.stderr)
        return 1

    print(
        "RichardOS Settings references are present in the pinned "
        "LineageOS Settings and Android framework sources."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
