#!/usr/bin/env python3
"""Audit RichardOS battery preferences against the pinned Lineage SDK API."""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

SETTINGS = {
    "STATUS_BAR_BATTERY_STYLE": "richardos_battery_style_values",
    "STATUS_BAR_SHOW_BATTERY_PERCENT": "richardos_battery_percent_values",
}


def extract_array(patch: str, name: str) -> list[str] | None:
    match = re.search(
        rf'<string-array\s+name="{re.escape(name)}">(.*?)</string-array>',
        patch,
        re.DOTALL,
    )
    if not match:
        return None
    return re.findall(r"<item>\s*(.*?)\s*</item>", match.group(1), re.DOTALL)


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
    arrays_section = patch.split(
        "diff --git a/res/values/richardos_arrays.xml", 1
    )
    arrays_text = (
        arrays_section[1].split("\ndiff --git ", 1)[0]
        if len(arrays_section) == 2
        else ""
    )

    for name, array_name in SETTINGS.items():
        declaration = re.compile(
            rf"public\s+static\s+final\s+String\s+{name}\s*="
        )
        if not declaration.search(sdk):
            print(f"missing Lineage SDK declaration: {name}", file=sys.stderr)
            failed = True
        if f"LineageSettings.System.{name}" not in patch:
            print(f"RichardOS patch does not use SDK constant: {name}", file=sys.stderr)
            failed = True

        validator = re.search(
            rf"{name}_VALIDATOR\s*=\s*new InclusiveIntegerRangeValidator\(\s*(\d+)\s*,\s*(\d+)\s*\)",
            sdk,
        )
        if not validator:
            print(f"missing supported integer range for {name}", file=sys.stderr)
            failed = True
            continue

        minimum, maximum = map(int, validator.groups())
        expected = [str(value) for value in range(minimum, maximum + 1)]
        actual = extract_array(arrays_text, array_name)
        if actual != expected:
            print(
                f"{array_name} must match Lineage SDK range {minimum}..{maximum}; "
                f"found {actual}",
                file=sys.stderr,
            )
            failed = True

    if failed:
        return 1
    print("RichardOS battery keys and preference values match the checked-out Lineage SDK API.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
