#!/usr/bin/env python3
"""Conservative static index of Soong modules and declared module dependencies.

This is a source-text preflight, not a replacement for Soong/Blueprint parsing.
Only the supplied Android.bp files are indexed; missing names may live in
other namespaces or projects that were not supplied.
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

TOKEN_RE = re.compile(
    r'(?P<space>\s+)|(?P<line>//[^\n]*)|(?P<block>/\*[\s\S]*?\*/)|'
    r'(?P<string>"(?:\\.|[^"\\])*")|'
    r"(?P<ident>[A-Za-z_][A-Za-z0-9_.-]*)|(?P<symbol>[^\s])"
)
DEPENDENCY_PROPERTIES = {
    "defaults",
    "shared_libs",
    "static_libs",
    "whole_static_libs",
    "header_libs",
    "runtime_libs",
    "jni_libs",
    "uses_libs",
    "optional_uses_libs",
    "required",
}


@dataclass
class Module:
    name: str
    module_type: str
    source: Path
    dependencies: dict[str, list[str]] = field(default_factory=dict)


def tokenize(text: str) -> list[str]:
    tokens: list[str] = []
    for match in TOKEN_RE.finditer(text):
        kind = match.lastgroup
        if kind in {"space", "line", "block"}:
            continue
        value = match.group()
        if kind == "string":
            # Decode only the common escaped quote/backslash forms.
            value = value[1:-1].replace(r'\"', '"').replace(r"\\", "\\")
        tokens.append("STR:" + value if kind == "string" else value)
    return tokens


def matching_brace(tokens: list[str], start: int) -> int | None:
    depth = 0
    for index in range(start, len(tokens)):
        if tokens[index] == "{":
            depth += 1
        elif tokens[index] == "}":
            depth -= 1
            if depth == 0:
                return index
    return None


def parse_modules(path: Path) -> list[Module]:
    tokens = tokenize(path.read_text(encoding="utf-8", errors="replace"))
    modules: list[Module] = []
    index = 0
    while index + 1 < len(tokens):
        if tokens[index + 1] != "{" or not re.fullmatch(
            r"[A-Za-z_][A-Za-z0-9_.-]*", tokens[index]
        ):
            index += 1
            continue
        end = matching_brace(tokens, index + 1)
        if end is None:
            raise ValueError(f"{path}: unterminated block beginning at token {index}")
        module_type = tokens[index]
        body_start = index + 2
        name: str | None = None
        deps: dict[str, list[str]] = {}
        depth = 1
        cursor = body_start
        while cursor < end:
            token = tokens[cursor]
            if token == "{":
                depth += 1
                cursor += 1
                continue
            if token == "}":
                depth -= 1
                cursor += 1
                continue
            if cursor + 1 < end and tokens[cursor + 1] == ":":
                prop = token
                value_index = cursor + 2
                if depth == 1 and prop == "name" and value_index < end:
                    if tokens[value_index].startswith("STR:"):
                        name = tokens[value_index][4:]
                if prop in DEPENDENCY_PROPERTIES and value_index < end and tokens[value_index] == "[":
                    array_depth = 0
                    values: list[str] = []
                    scan = value_index
                    while scan < end:
                        current = tokens[scan]
                        if current == "[":
                            array_depth += 1
                        elif current == "]":
                            array_depth -= 1
                            if array_depth == 0:
                                break
                        elif array_depth == 1 and current.startswith("STR:"):
                            values.append(current[4:])
                        scan += 1
                    deps.setdefault(prop, []).extend(values)
                cursor += 1
                continue
            cursor += 1
        if name:
            modules.append(Module(name, module_type, path, deps))
        index = end + 1
    return modules


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("android_bp", nargs="+", type=Path, help="Android.bp files to index")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="return status 1 when dependencies are absent from the supplied files",
    )
    args = parser.parse_args()

    modules: list[Module] = []
    for path in args.android_bp:
        if not path.is_file():
            print(f"ERROR missing Android.bp: {path}", file=sys.stderr)
            return 2
        try:
            modules.extend(parse_modules(path))
        except OSError as exc:
            print(f"ERROR cannot read {path}: {exc}", file=sys.stderr)
            return 2
        except ValueError as exc:
            print(f"ERROR malformed Android.bp: {exc}", file=sys.stderr)
            return 2

    if not modules:
        print("ERROR no named Soong modules were found in supplied files.", file=sys.stderr)
        return 2

    by_name: dict[str, list[Module]] = {}
    for module in modules:
        by_name.setdefault(module.name, []).append(module)

    duplicates = {name: entries for name, entries in by_name.items() if len(entries) > 1}
    unresolved: list[tuple[Module, str, str]] = []
    reference_count = 0
    for module in modules:
        for prop, names in module.dependencies.items():
            for dependency in names:
                reference_count += 1
                if dependency not in by_name:
                    unresolved.append((module, prop, dependency))

    print(f"Soong source index: {len(args.android_bp)} Android.bp file(s)")
    print(f"Named modules indexed: {len(modules)}")
    print(f"Dependency references inspected: {reference_count}")
    print(f"Names declared more than once in supplied files: {len(duplicates)}")
    for name, entries in sorted(duplicates.items()):
        locations = ", ".join(str(item.source) for item in entries)
        print(f"DUPLICATE {name}: {locations}")
    print(f"Dependencies not found in supplied files: {len(unresolved)}")
    for module, prop, dependency in unresolved:
        print(f"UNINDEXED {module.name} ({module.source}) {prop}: {dependency}")

    print(
        "Note: unindexed names may be valid modules from other Android.bp files, "
        "Soong namespaces, or external projects."
    )
    print(
        "This source-text scan does not evaluate Blueprint expressions, defaults, "
        "visibility, variants, namespaces, ABI, or the final Soong graph."
    )
    if args.strict and unresolved:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
