<div align="center">

<img src="vendor/richardos/branding/richardos-lion.svg" alt="RichardOS lion emblem" width="180" />

# RichardOS

**A LineageOS-based Android operating system for Xiaomi Redmi Note 10**

`mojito` · Snapdragon 678 · ARM64

*Your Android. Your rules.*

</div>

> **Project status:** early development / device bring-up. The repository contains inherited device-source mappings and static audit tools. No RichardOS build has been completed or boot-tested yet. No installable ZIP is available.

## Vision

RichardOS is intended to become a full Android operating system with a coherent **Material You** design language, its own system applications, settings, update experience, and device-specific integration.

The initial target is Xiaomi Redmi Note 10 (`mojito`). The project uses LineageOS as its Android platform foundation; it is not affiliated with LineageOS or Xiaomi.

## Design goals

- Material You-inspired interface and dynamic color support.
- Consistent system UI, quick settings, lock screen, and settings experience.
- A curated set of RichardOS system applications.
- Reliable OTA/update infrastructure.
- Performance, battery-life, and hardware compatibility as priorities.
- Security features enabled by default, including SELinux enforcing where supported.

## Device

| Property | Target |
|---|---|
| Device | Xiaomi Redmi Note 10 4G |
| Codename | `mojito` |
| SoC | Qualcomm Snapdragon 678 |
| Architecture | ARM64 |
| Platform baseline | LineageOS 24.0 (Android 17) |
| Kernel/device/vendor sources | See [DEVICE_SOURCES.md](docs/DEVICE_SOURCES.md) and [manifest](manifests/mojito-lineage24.xml) |

The inherited source manifest pins candidate device, kernel, and vendor repositories to immutable revisions. A successful sync or static audit does not prove that the target builds or boots.

## Repository layout

- `manifests/` — local Android repo manifests.
- `scripts/` — source audits, guarded device-tree fix, and build helper.
- `tests/` — unit tests for the helper scripts.
- `docs/` — device-source notes, design specification, branding guide, and project documentation.
- `vendor/richardos/config/` — RichardOS product branding layer for integration into the mojito product makefile.
- `vendor/richardos/branding/` — original RichardOS logo assets.
- `patches/lineage/Settings/` — native Settings integration patch for LineageOS 24.0.

## Current roadmap

1. Re-audit the inherited device sources and manifest against LineageOS 24.0 / Android 17.
2. Sync the Android platform and run static preflight checks when suitable storage is available.
3. Build an unmodified LineageOS baseline for `mojito`.
4. Boot-test the baseline and validate core hardware.
5. Implement the first RichardOS SystemUI and Settings customizations.
6. Add RichardOS applications, settings, and update infrastructure.
7. Publish reproducible builds, checksums, changelogs, and known issues.

The initial interface and feature direction is documented in [RICHARDOS_DESIGN.md](docs/RICHARDOS_DESIGN.md). The lion mark and palette are documented in [BRANDING.md](docs/BRANDING.md). The first native Settings dashboard patch is documented in [SETTINGS_INTEGRATION.md](docs/SETTINGS_INTEGRATION.md).

## Apply the Settings customization

After syncing the target Settings repository on the `lineage-24.0` branch, apply the experimental RichardOS dashboard patch:

```bash
bash scripts/apply-settings-patch.sh /path/to/lineage/packages/apps/Settings
```

The helper checks the repository remote, branch, and working-tree cleanliness, then runs `git apply --check` before applying. The dashboard is an in-Settings entry, not a separate application. Its Status Bar and Lock Screen sections are placeholders; Root & System contains read-only device/security diagnostics. The Monet selector applies curated seed colors through Android's existing SystemUI theme customization setting and can restore wallpaper-derived colors. This has not yet been compiled or tested on-device. Review the resulting diff and compile Settings before using it in a ROM.

## Build preparation

A Linux x86_64 build host is required. Android builds are large; plan for at least 32 GB RAM and roughly 350 GB of free SSD space.

Install the Android `repo` tool and required build dependencies, then run:

```bash
bash scripts/build.sh "$HOME/android/richardos-mojito"
```

The helper runs the repository's unit tests, validates the local manifest, syncs LineageOS and the device sources, performs static source/VINTF checks, and starts the baseline build. These checks do not replace a successful Android build or physical-device testing.

Long-running work should be run inside `tmux` so it survives SSH disconnections.

## Safety

Do not flash experimental images unless they are explicitly built for `mojito`, their checksums are verified, and the installation procedure has been tested. Keep an independent backup. Never publish signing keys, passwords, or private credentials.

## Licensing

Original scripts and documentation retain their applicable notices. Android platform code, LineageOS components, device trees, kernel sources, and proprietary vendor files retain their upstream licenses and redistribution restrictions. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
