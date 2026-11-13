<div align="center">

<img src="vendor/richardos/branding/richardos-lion.svg" alt="RichardOS lion emblem" width="180" />

# RichardOS

**A LineageOS-based Android project: experimental ARM64 GSI first, Redmi Note 10 port maintained separately**

`mojito` · Snapdragon 678 · ARM64

*Your Android. Your rules.*

</div>

> **Project status:** early development / device bring-up. The repository contains inherited device-source mappings and static audit tools. No RichardOS build has been completed or boot-tested yet. No installable ZIP is available.

## Vision

RichardOS is intended to become a full Android operating system with a coherent **Material You** design language, its own system applications, settings, update experience, and device-specific integration.

The current priority is an experimental ARM64 GSI for compatibility research and tester feedback. Xiaomi Redmi Note 10 (`mojito`) remains a separate device-specific port. The project uses LineageOS as its Android platform foundation; it is not affiliated with LineageOS or Xiaomi.

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

- `gsi/` — experimental GSI target metadata, compatibility intake and tester guidance. No GSI image has been built yet.
- `manifests/` — local Android repo manifests.
- `scripts/` — source audits, guarded device-tree fix, and build helper.
- `tests/` — unit tests for the helper scripts.
- `docs/` — device-source notes, design specification, branding guide, and project documentation.
- `vendor/richardos/config/` — RichardOS product branding layer for integration into the mojito product makefile.
- `vendor/richardos/branding/` — approved lion mark and original wallpaper SVG masters.
- `vendor/richardos/overlay/` — warm-gold Material You palette overlay.
- `vendor/richardos/wallpapers/` — WallpaperPicker2 partner APK source.
- `scripts/render-wallpapers.sh` — render wallpaper masters to PNG previews.
- `scripts/install-system-branding.sh` — install product identity, palette, and generated lion boot animation.
- `scripts/install-wallpaper-overlay.sh` — install Nocturne as the framework default wallpaper.
- `scripts/install-wallpaper-picker.sh` — add all three wallpapers to WallpaperPicker2.
- `patches/lineage/Settings/` — native Settings integration patch for LineageOS 24.0.

## Current roadmap

1. Validate the LineageOS 24.0 generic ARM64 GSI product and exact lunch alias.
2. Build and inspect an unmodified generic GSI baseline in a suitable development environment.
3. Integrate RichardOS branding and Settings customizations without importing `mojito` hardware dependencies.
4. Validate the resulting image and document known limitations before any tester release.
5. Collect device compatibility reports through the GSI tester intake.
6. Continue the separate Redmi Note 10 (`mojito`) port.

The first clean baseline compilation procedure is documented in [FIRST_BUILD.md](docs/FIRST_BUILD.md); use `scripts/build-baseline.sh` before applying RichardOS branding or the experimental Settings patch. The initial interface and feature direction is documented in [RICHARDOS_DESIGN.md](docs/RICHARDOS_DESIGN.md). The lion mark, graphite/gold identity, original wallpaper artwork, and framework default-wallpaper overlay installer are documented in [BRANDING.md](docs/BRANDING.md). The first native Settings dashboard patch is documented in [SETTINGS_INTEGRATION.md](docs/SETTINGS_INTEGRATION.md).

## Apply the Settings customization

After syncing the target Settings repository on the `lineage-24.0` branch, apply the experimental RichardOS dashboard patch:

```bash
bash scripts/apply-settings-patch.sh /path/to/lineage/packages/apps/Settings
```

The helper checks the repository remote, branch, and working-tree cleanliness, then runs `git apply --check` before applying. The dashboard is an in-Settings entry, not a separate application. Its Status Bar section contains Lineage battery controls, Lock Screen links to native lock-screen notification settings, and Root & System contains read-only device/security diagnostics. The Monet selector applies curated seed colors through Android's existing theme customization setting; System default removes RichardOS overrides and restores wallpaper-derived colors. This has not yet been compiled or tested on-device. Review the resulting diff and compile Settings before using it in a ROM.

## Run source-level tests

The lightweight Python test suite can be run before syncing or building Android:

```bash
python3 -m unittest discover -s tests -v
```

The SetupWizard branding tests parse the RichardOS XML overlays, check resource-name
uniqueness within each values file, and verify that the welcome and finish layouts
use the lion drawable generated by the branding installer. GitHub Actions also
checks out the upstream LineageOS Settings `lineage-24.0` branch, applies the
RichardOS Settings patch in the temporary runner, and runs `git diff --check`
on the result. These checks validate source integration and repository files;
they do not replace Android resource compilation or a full ROM build.

## Build preparation

A Linux x86_64 build host is required. Plan for at least 8 CPU threads, 32 GB RAM, and 350 GB of free SSD space before sync (80 GB after sync). `scripts/check-build-host.sh` performs a read-only preflight before either build stage.

Install the Android `repo` tool and required build dependencies, then run:

```bash
bash scripts/build-baseline.sh "$HOME/android/richardos-mojito"
```

The baseline helper runs the repository's unit tests, validates the local manifest and existing source checkout, records the resolved manifest, applies the guarded VINTF correction, audits vendor source paths and VINTF, then compiles the unbranded LineageOS baseline. It does not sync automatically; initialize and sync the source tree using the steps in FIRST_BUILD.md. Apply RichardOS product branding, boot animation, palette, wallpapers, and Settings patch only after the baseline is established. After that baseline succeeds, run `bash scripts/build.sh "$HOME/android/richardos-mojito"` for the RichardOS customization stage; it applies the native Settings Hub patch as well as the branding and wallpaper integrations before rebuilding. The branding installer requires `rsvg-convert` and `zip`; wallpaper rendering also supports Inkscape. These checks do not replace a successful Android build or physical-device testing.

Long-running work should be run inside `tmux` so it survives SSH disconnections.

## Safety

Do not flash experimental images unless they are explicitly built for `mojito`, their checksums are verified, and the installation procedure has been tested. Keep an independent backup. Never publish signing keys, passwords, or private credentials.

## Licensing

Original scripts and documentation retain their applicable notices. Android platform code, LineageOS components, device trees, kernel sources, and proprietary vendor files retain their upstream licenses and redistribution restrictions. See [LICENSE](LICENSE) and [NOTICE](NOTICE).


## Experimental GSI

RichardOS is prioritizing the generic ARM64 GSI. See [GSI preparation](gsi/README.md) and [tester intake](gsi/GSI_TESTING.md). Repository CI validates only target metadata and source files; it does not compile Android. There is no downloadable GSI image or approved device list yet.
