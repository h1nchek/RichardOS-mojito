#!/usr/bin/env python3
"""Check that RichardOS uses battery settings exposed by the pinned Lineage SDK."""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

CONSTANTS = (
    "STATUS_BAR_BATTERY_STYLE",
    "STATUS_BAR_SHOW_BATTERY_PERCENT",
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("sdk_source", type=pathlib.Path)
    parser.add_argument("settings_patch", type=pathlib.Path)
    args = parser.parse_args()

    try:
        sdk = args.sdk_source.read_text(encoding="utf-8")
        patch = args.settings_patch.read_text(encoding="utf-8")
    except OSError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    failed = False
    for name in CONSTANTS:
        declaration = re.compile(
            rf"public\s+static\s+final\s+String\s+{name}\s*="
        )
        if not declaration.search(sdk):
            print(f"missing Lineage SDK declaration: {name}", file=sys.stderr)
            failed = True
        if f"LineageSettings.System.{name}" not in patch:
            print(f"RichardOS patch does not use SDK constant: {name}", file=sys.stderr)
            failed = True

    if failed:
        return 1
    print("RichardOS battery settings match the checked-out Lineage SDK API.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
