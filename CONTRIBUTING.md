# Contributing to BlueOS-mojito

Thanks for helping with the Redmi Note 10 (mojito/sunny) port.

## Before making changes

- Read [the build guide](docs/BUILDING.md) and [device source audit](docs/DEVICE_SOURCES.md).
- Keep device-specific changes separate from upstream BlueOS changes.
- Do not assume that a source-level audit proves build or hardware compatibility.
- Open an issue or discussion before large architectural changes.

## Build prerequisites

A full Android build needs a Linux x86_64 host. The current project build workflow expects at least 32 GiB RAM, 350 GiB free SSD space, the Android `repo` tool, Git, Python 3, Java, and the standard LineageOS build packages. These are practical minimums, not a guarantee that every build will fit.

Follow [docs/BUILDING.md](docs/BUILDING.md). Build the clean LineageOS stage first, then use a separate checkout for BlueOS. Do not mix the two source directories.

## Pre-submission checks

Run from the repository root:

```bash
python3 -m py_compile scripts/*.py tests/*.py
bash -n scripts/build.sh
python3 scripts/audit_repo_manifests.py manifests/*.xml
python3 -m unittest discover -s tests -v
```

If you change device makefiles, vendor files, VINTF declarations, or manifests, explain what was changed and which source revision it targets.

## Pull requests

- Use a focused branch and submit a pull request to `main`.
- Describe the problem, the change, and the exact files or source revisions affected.
- Include relevant command output or build-log excerpts; redact tokens, private URLs, serial numbers, and other secrets.
- State clearly whether a result is statically inspected, compiled, or tested on hardware.
- Do not mark a build as successful unless the complete command finished successfully.
- Do not commit generated Android output, proprietary firmware dumps, private signing keys, runner registration tokens, or credentials.

## Attribution

Credit contributors for substantive work such as device-tree fixes, build-system changes, patch compatibility work, and verified builds. A build-only contribution should be described as build assistance rather than authorship of the entire port.
