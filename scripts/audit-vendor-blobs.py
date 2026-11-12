#!/usr/bin/env python3
"""Audit proprietary PRODUCT_COPY_FILES source paths in a synced Android tree.

Run from any directory:
  python3 scripts/audit-vendor-blobs.py /path/to/android/tree

The script checks source-side paths only; it does not validate ELF ABI,
firmware compatibility, licenses, or runtime behavior.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

DEFAULT_MAKEFILES = (
    "vendor/xiaomi/mojito/mojito-vendor.mk",
    "vendor/xiaomi/sm6150-common/sm6150-common-vendor.mk",
)
COPY_ENTRY = re.compile(r"^\s*([^\s#]+):([^\s\\]+)")


def collect_entries(makefile: Path) -> list[str]:
    entries: list[str] = []
    logical = ""
    for raw in makefile.read_text(errors="replace").splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line:
            continue
        continued = line.endswith("\\")
        logical += (" " if logical else "") + (line[:-1].rstrip() if continued else line)
        if continued:
            continue
        if logical.lstrip().startswith("PRODUCT_COPY_FILES"):
            payload = re.sub(r"^\s*PRODUCT_COPY_FILES\s*(?:\+=|:=|=)\s*", "", logical)
            for token in payload.split():
                match = COPY_ENTRY.match(token)
                if match:
                    entries.append(match.group(1))
        logical = ""
    if logical and logical.lstrip().startswith("PRODUCT_COPY_FILES"):
        payload = re.sub(r"^\s*PRODUCT_COPY_FILES\s*(?:\+=|:=|=)\s*", "", logical)
        for token in payload.split():
            match = COPY_ENTRY.match(token)
            if match:
                entries.append(match.group(1))
    return entries


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("android_tree", type=Path, help="root of the synced Android source tree")
    parser.add_argument(
        "--makefile", action="append", default=None,
        help="PRODUCT_COPY_FILES makefile path relative to tree (repeatable)",
    )
    args = parser.parse_args()
    root = args.android_tree.resolve()
    makefiles = args.makefile or list(DEFAULT_MAKEFILES)

    missing_makefiles = [name for name in makefiles if not (root / name).is_file()]
    if missing_makefiles:
        for name in missing_makefiles:
            print(f"ERROR missing makefile: {name}", file=sys.stderr)
        return 2

    checked: list[tuple[str, bool]] = []
    unresolved: list[str] = []
    for name in makefiles:
        for source in collect_entries(root / name):
            if "$(" in source or "${" in source:
                unresolved.append(f"{name}: {source}")
                continue
            checked.append((source, (root / source).is_file()))

    found = sum(exists for _, exists in checked)
    missing = [(path, exists) for path, exists in checked if not exists]
    print(f"Vendor blob source audit: {root}")
    print(f"References checked: {len(checked)}")
    print(f"Present: {found}")
    print(f"Missing: {len(missing)}")
    print(f"Unresolved variable paths: {len(unresolved)}")
    for path, _ in missing:
        print(f"MISSING  {path}")
    for item in unresolved:
        print(f"UNRESOLVED  {item}")
    if not checked:
        print("ERROR: no concrete PRODUCT_COPY_FILES source paths were parsed.", file=sys.stderr)
        return 2
    # Never report a clean audit when some source paths could not be resolved.
    if unresolved:
        return 2
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
