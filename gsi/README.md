# RichardOS Experimental GSI

**Status: preparation only — no image has been built or validated.**

RichardOS is prioritizing an experimental ARM64 Generic System Image (GSI) for compatibility research and controlled tester feedback. The existing Redmi Note 10 (`mojito`) device port remains separate and is not the GSI target.

## Initial target

- Platform branch: LineageOS `lineage-24.0`
- Architecture: ARM64 userspace, 64-bit Binder
- Upstream product definition: `device/generic/common/gsi_arm64.mk`
- Expected output class: generic ARM64 system image
- Build variant intended for development validation: `userdebug`

The LineageOS 24.0 generic device tree currently contains `gsi_arm64.mk`. The exact lunch alias and complete build integration must be confirmed from a synced source tree before attempting a build; this repository deliberately does not invent a product makefile or fork upstream GSI definitions.

## Design boundary

The GSI supplies the Android system side. Each phone still relies on its own compatible vendor implementation, firmware, kernel and device configuration. ARM64 alone does not establish compatibility. A device must meet Android Treble/GSI requirements and be assessed individually.

RichardOS-specific changes should be layered onto the generic product only after the unmodified upstream GSI target is confirmed to build. Keep device-specific Xiaomi files out of the generic target.

## Milestones

1. **Repository preparation** — target metadata, compatibility intake and issue templates.
2. **Source validation** — sync the intended LineageOS branch and confirm the GSI product and lunch alias.
3. **Baseline build** — build an unmodified generic ARM64 GSI in a suitable development environment.
4. **RichardOS integration** — add shared branding and Settings changes incrementally, with CI checks.
5. **Internal validation** — inspect build output and test in a controlled environment before recruiting device testers.
6. **Limited tester programme** — publish only a verified build, checksums, known issues and clear risk information.

## Tester safety and reporting

Do not distribute an unbuilt, unverified or experimental image as ready to install. GSI testing can cause data loss or leave a device unusable. No universal installation procedure applies to every phone; device-specific eligibility and recovery planning must be reviewed by a knowledgeable adult before any real-device test. Do not use a daily-use phone or any device containing important data as an early test device.

Use the [GSI compatibility intake](GSI_TESTING.md) and [bug report template](../.github/ISSUE_TEMPLATE/gsi_bug_report.yml) to collect model, Android/vendor version, observed behaviour and logs with personal information removed.

## Upstream references

- [LineageOS generic device tree, lineage-24.0](https://github.com/LineageOS/android_device_generic_common/tree/lineage-24.0)
- [LineageOS ARM64 GSI product definition](https://github.com/LineageOS/android_device_generic_common/blob/lineage-24.0/gsi_arm64.mk)
- [Android GSI overview and compatibility requirements](https://source.android.com/docs/core/tests/vts/gsi)
