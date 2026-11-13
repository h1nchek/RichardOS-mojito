# RichardOS Experimental GSI

**Release track: 0.9.0 pre-release**  
**Status: preparation only — no image has been built or validated.**

RichardOS 0.9.0 is the experimental GSI track. Its purpose is to establish the shared system experience, collect compatibility feedback and fix issues before the first stable release. It is not the finished RichardOS operating system.

The Redmi Note 10 (mojito) device port is intentionally deferred to the **1.0.0 stable release**. Do not merge device-specific Xiaomi configuration into the generic GSI target.

## Release policy

- **0.9.0 pre-release:** experimental GSI development, compatibility research, tester feedback and bug fixing.
- **1.0.0 stable:** planned stable milestone. The separate mojito port is planned for this release cycle, subject to build and device validation.
- Pre-release builds, if and when produced, must use explicit identifiers such as 0.9.0-pre.1; do not label an unbuilt artifact as a release.
- No public binary is available yet. This repository currently contains preparation files only.

## Initial target

- Platform branch: LineageOS lineage-24.0
- Architecture: ARM64 userspace, 64-bit Binder
- Upstream product definition: device/generic/common/gsi_arm64.mk
- Intended development variant: userdebug

The LineageOS 24.0 generic device tree contains the ARM64 GSI product definition. The exact lunch alias and build integration must be confirmed against the complete synced source tree before a build is attempted. The repository does not invent or replace upstream product definitions.

## Design boundary

The GSI provides the Android system side. Each phone still relies on its own compatible vendor implementation, firmware, kernel and device configuration. ARM64 alone does not establish compatibility. Treble support, vendor compatibility and device-specific constraints must be assessed individually.

RichardOS features should be integrated incrementally on top of a verified generic baseline. Keep device-specific Xiaomi files out of the generic target.

## 0.9.0 milestones

1. Repository preparation — target metadata, compatibility intake and issue templates.
2. Source validation — confirm the upstream product definition and exact build target.
3. Baseline validation — build an unmodified generic ARM64 image in a suitable development environment.
4. RichardOS integration — add shared branding and Settings changes incrementally.
5. Internal quality checks — review build-critical configuration, build output, known issues and release notes.
6. Pre-release candidate — only after a real artifact exists, publish its checksum and exact limitations for controlled testing.
7. Tester feedback — triage reports and publish fixes as new pre-release versions.

## Tester safety and reporting

Do not distribute an unbuilt, unverified or experimental image as ready to install. GSI testing can cause data loss or leave a device unusable. Device compatibility and recovery planning must be reviewed before any real-device test. Do not use a daily-use phone or a device containing important data as an early test device.

Use the GSI compatibility intake (GSI_TESTING.md) and bug report template. Remove personal information from logs and screenshots.

## Upstream references

- https://github.com/LineageOS/android_device_generic_common/tree/lineage-24.0
- https://github.com/LineageOS/android_device_generic_common/blob/lineage-24.0/gsi_arm64.mk
- https://developer.android.com/topic/generic-system-image
