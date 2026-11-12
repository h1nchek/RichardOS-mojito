#!/usr/bin/env python3
"""Validate local Android repo manifest XML before syncing source trees.

Structural preflight only: repo remains authoritative for full manifest
semantics, remote resolution, project fetching, and revision availability.
"""
from __future__ import annotations

import argparse
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def validate_manifest(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        root = ET.parse(path).getroot()
    except (ET.ParseError, OSError) as exc:
        return [f"{path}: cannot parse XML: {exc}"]
    if root.tag != "manifest":
        return [f"{path}: root element must be <manifest>"]

    remotes = {node.get("name") for node in root.findall("remote") if node.get("name")}
    default = root.find("default")
    default_remote = default.get("remote") if default is not None else None
    seen_paths: dict[str, str] = {}

    for project in root.findall("project"):
        name = project.get("name")
        project_path = project.get("path") or name
        revision = project.get("revision")
        remote = project.get("remote") or default_remote
        if not name:
            errors.append(f"{path}: <project> is missing name")
            continue
        if not project_path:
            errors.append(f"{path}: project {name!r} has no usable path")
        elif project_path in seen_paths:
            errors.append(f"{path}: duplicate project path {project_path!r} "
                          f"({seen_paths[project_path]!r} and {name!r})")
        else:
            seen_paths[project_path] = name
        if not revision:
            errors.append(f"{path}: project {name!r} is missing revision")
        if remote and remote not in remotes:
            errors.append(f"{path}: project {name!r} references undeclared remote {remote!r}")

    for extension in root.findall("extend-project"):
        if not extension.get("name"):
            errors.append(f"{path}: <extend-project> is missing required name")
        if not (extension.get("path") or extension.get("name")):
            errors.append(f"{path}: <extend-project> needs path or name")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifests", nargs="+", type=Path)
    args = parser.parse_args()
    errors = []
    for path in args.manifests:
        current = validate_manifest(path)
        if current:
            errors.extend(current)
        else:
            print(f"OK: {path}")
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
