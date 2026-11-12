#!/usr/bin/env python3
"""Verify local manifest extensions against the selected LineageOS manifest."""
from __future__ import annotations

import argparse
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

REQUIRED_LOCAL_PATHS = {
    "device/qcom/sepolicy",
    "device/qcom/sepolicy_vndr",
    "hardware/xiaomi",
    "hardware/qcom-caf/bootctrl",
    "hardware/qcom-caf/common",
    "hardware/qcom-caf/sm8150/audio",
    "hardware/qcom-caf/sm8150/display",
    "hardware/qcom-caf/sm8150/media",
    "hardware/qcom-caf/wlan",
    "vendor/qcom/opensource/usb",
    "vendor/qcom/opensource/dataservices",
    "vendor/qcom/opensource/commonsys-intf/display",
    "vendor/qcom/opensource/display",
    "vendor/qcom/opensource/interfaces",
}


def load(path: Path):
    try:
        return ET.parse(path).getroot()
    except (ET.ParseError, OSError) as exc:
        raise ValueError(f"{path}: cannot parse manifest: {exc}") from exc


def audit(local_path: Path, upstream_paths: list[Path]) -> list[str]:
    errors: list[str] = []
    local = load(local_path)
    upstream_projects: set[tuple[str, str]] = set()
    for upstream_path in upstream_paths:
        root = load(upstream_path)
        for project in root.findall("project"):
            name = project.get("name")
            path = project.get("path") or name
            if name and path:
                upstream_projects.add((name, path))

    local_paths: set[str] = set()
    for project in local.findall("project"):
        name = project.get("name")
        path = project.get("path") or name
        if path:
            local_paths.add(path)

    for extension in local.findall("extend-project"):
        name = extension.get("name")
        path = extension.get("path") or name
        if not name or not path:
            continue
        if (name, path) not in upstream_projects:
            errors.append(
                f"extend-project {name!r} at {path!r} does not match a project "
                "in the selected upstream manifest"
            )
        local_paths.add(path)

    missing = sorted(REQUIRED_LOCAL_PATHS - local_paths)
    for path in missing:
        errors.append(f"required device dependency is absent from local manifest: {path}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("local_manifest", type=Path)
    parser.add_argument("upstream_manifests", nargs="+", type=Path)
    args = parser.parse_args()
    try:
        errors = audit(args.local_manifest, args.upstream_manifests)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("OK: local manifest extensions match upstream project names and paths.")
    print(f"OK: all {len(REQUIRED_LOCAL_PATHS)} required local device dependency paths are declared.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
