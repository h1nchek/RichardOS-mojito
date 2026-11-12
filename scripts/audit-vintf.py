#!/usr/bin/env python3
"""Perform a conservative XML preflight on Android VINTF manifest/matrix files.

This checks XML well-formedness and a few structural invariants only. It does
not replace checkvintf or prove framework/vendor compatibility.
"""
from __future__ import annotations

import argparse
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ALLOWED_ROOTS = {"manifest", "compatibility-matrix"}


def audit(path: Path) -> tuple[list[str], int]:
    errors: list[str] = []
    try:
        root = ET.parse(path).getroot()
    except (ET.ParseError, OSError) as exc:
        return [f"{path}: XML parse failed: {exc}"], 0

    if root.tag not in ALLOWED_ROOTS:
        errors.append(
            f"{path}: unexpected root <{root.tag}> "
            f"(expected <manifest> or <compatibility-matrix>)"
        )
        return errors, 0

    hal_count = 0
    seen_fqnames: set[tuple[str, str]] = set()
    for hal in root.findall("hal"):
        hal_count += 1
        names = [
            (node.text or "").strip()
            for node in hal.findall("name")
            if (node.text or "").strip()
        ]
        if not names:
            errors.append(f"{path}: <hal> entry #{hal_count} has no <name>")
            continue
        fqnames = [(node.text or "").strip() for node in hal.findall("fqname")]
        for fqname in fqnames:
            if not fqname:
                errors.append(f"{path}: HAL entry #{hal_count} has an empty <fqname> entry")

        # Some legacy manifests group multiple HAL names in one <hal>. Their
        # FQName-to-name mapping is ambiguous, so avoid a false duplicate claim.
        if len(names) != 1:
            continue
        name = names[0]
        for fqname in fqnames:
            if not fqname:
                continue
            key = (name, fqname)
            if key in seen_fqnames:
                errors.append(
                    f"{path}: duplicate HAL instance {name} {fqname}"
                )
            seen_fqnames.add(key)

    return errors, hal_count


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("xml_files", nargs="+", type=Path, help="VINTF XML files")
    args = parser.parse_args()

    total_hals = 0
    failed = False
    for path in args.xml_files:
        errors, hal_count = audit(path)
        total_hals += hal_count
        if errors:
            failed = True
            for error in errors:
                print(f"ERROR {error}")
        else:
            print(f"OK {path}: well-formed VINTF XML; HAL entries: {hal_count}")

    print(f"Files checked: {len(args.xml_files)}")
    print(f"HAL entries parsed: {total_hals}")
    print("Result: issues found" if failed else "Result: structural preflight passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
