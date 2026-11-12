#!/usr/bin/env python3
"""Validate the basic structure and CRCs of a candidate Android OTA ZIP."""
from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path

OTA_MARKERS = {
    "payload.bin",
    "META-INF/com/android/metadata",
    "META-INF/com/google/android/update-binary",
}


def validate(path: Path) -> None:
    if not path.is_file() or not zipfile.is_zipfile(path):
        raise ValueError(f"not a valid ZIP archive: {path}")
    try:
        with zipfile.ZipFile(path) as archive:
            names = set(archive.namelist())
            bad_member = archive.testzip()
    except (OSError, zipfile.BadZipFile) as exc:
        raise ValueError(f"cannot read ZIP archive {path}: {exc}") from exc
    if bad_member is not None:
        raise ValueError(f"ZIP CRC check failed for member: {bad_member}")
    if not names.intersection(OTA_MARKERS):
        raise ValueError(
            f"no recognized Android OTA marker found in archive: {path}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("zip", type=Path, help="candidate Android OTA ZIP")
    args = parser.parse_args()
    try:
        validate(args.zip)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"Validated Android OTA ZIP structure and CRCs: {args.zip}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
