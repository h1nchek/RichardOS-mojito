# RichardOS 0.9.0 — universal GSI execution plan

**Branch:** `gsi/0.9.0-expansion`  
**Status:** source-verified planning and build preparation; no GSI build or device boot is claimed.

This document separates the universal GSI from the existing Redmi Note 10 (`mojito`) bring-up. The GSI must not inherit Xiaomi device trees, kernel configuration, proprietary blobs, or device-specific overlays.

## 1. Verified upstream target

The LineageOS `android_device_generic_common` repository on branch `lineage-24.0` currently registers `gsi_arm64.mk` in `AndroidProducts.mk`. That product declares:

- `PRODUCT_NAME := gsi_arm64`
- `PRODUCT_DEVICE := generic_arm64`
- ARM64 userspace and 64-bit Binder
- system-as-root, VNDK enforcement, and compatible property override assumptions
- system, system_ext, and product GSI product inheritance

Upstream source references:

- https://github.com/LineageOS/android_device_generic_common/blob/lineage-24.0/AndroidProducts.mk
- https://github.com/LineageOS/android_device_generic_common/blob/lineage-24.0/gsi_arm64.mk

The exact build combo is verified as `gsi_arm64-userdebug`. AOSP documents this ARM64 GSI target, and the LineageOS `lineage-24.0` product registry includes `gsi_arm64.mk`. The build helper still checks the resolved product variables in the complete synced checkout before compilation.

## 2. First GSI baseline — no RichardOS changes

1. Prepare a dedicated Linux x86_64 build host using the GSI-specific sizing and preflight requirements in `docs/GSI_BASELINE_BUILD.md`.
2. Initialize and sync the LineageOS `lineage-24.0` source tree.
3. Confirm that the synced `device/generic/common/AndroidProducts.mk` registers `gsi_arm64.mk`.
4. Inspect `gsi_arm64.mk` and its inherited makefiles from the actual synced revision.
5. Run `source build/envsetup.sh` and select the verified `gsi_arm64-userdebug` combo. Confirm that it resolves to product `gsi_arm64`, device `generic_arm64` and variant `userdebug`; the build helper enforces these checks and records the selected target in the build log.
6. Build the upstream baseline without RichardOS branding, Settings patches, or `mojito` dependencies.
7. Verify the expected output exists, inspect its partition/image metadata, record the resolved repo manifest and SHA-256, and retain the complete build log.

**Stop conditions:** missing product registration, unresolved lunch target, unexpected product/device variables, failed build, missing artifact, or an image layout that does not match the upstream GSI product. Do not continue to RichardOS integration until the baseline passes.

## 3. RichardOS integration order

Apply one change set at a time, rebuilding after each stage:

1. Shared product identity and build properties that are appropriate for a generic system image.
2. Boot animation and generic branding assets.
3. Framework palette/resource overlays.
4. Settings Hub integration.
5. Wallpaper package and defaults.
6. Additional features only after the prior stage builds and passes smoke checks.

Keep hardware-specific features out of the generic target. In particular, do not ship device-specific battery, camera, fingerprint, radio, audio, or kernel controls unless they are genuinely supported by the generic base and are capability-gated.

For every stage, record the patch set, build result, artifact checksum, and known limitations.

## 4. Device compatibility intake

A device is a *candidate*, not a supported device, until a named RichardOS build has been tested and its report reviewed.

Collect:

- manufacturer and exact model identifier;
- codename, if known;
- current Android version and vendor build;
- Treble support evidence and architecture;
- system/vendor partition arrangement where known;
- tester's spare-device status;
- tested RichardOS build identifier and checksum;
- per-feature results: boot, display, Wi-Fi, Bluetooth, mobile data, calls, audio, camera, sensors, fingerprint, encryption, and power.

Never infer compatibility from ARM64 or `ro.treble.enabled` alone. Keep the existing tester guidance in `gsi/GSI_TESTING.md`; do not ask testers to alter security settings or erase data during intake. Any later installation test requires a device-specific recovery plan and appropriate adult oversight.

## 5. Support tiers

- **Official:** a named maintainer, repeatable build, reviewed test report, known-issues list, and a realistic update commitment.
- **Community:** a third-party maintainer owns device-specific changes and support; RichardOS does not imply official validation.
- **Experimental:** development-only; no daily-use or compatibility promise.

Do not add a device to the official list merely because it booted once.

## 6. Contributor onboarding

Before accepting device maintainers, publish and enforce:

- a device-port contribution guide;
- required source and licensing provenance;
- build and test evidence;
- a standard compatibility report;
- issue and pull-request templates;
- maintainer ownership and handover expectations.

A device maintainer owns device-specific source maintenance and first-line triage. The project lead owns shared GSI architecture, release policy, and review of cross-device changes.

## 7. 0.9.0 release gate

A `0.9.0-pre.N` artifact may be published only when all are true:

- upstream baseline builds from a recorded manifest;
- RichardOS changes build reproducibly on top of that baseline;
- artifact metadata and SHA-256 are published;
- known limitations and supported test scope are explicit;
- at least one controlled test report exists for the exact artifact;
- no claim of universal compatibility is made.

The existing `mojito` port remains a separate device-specific workstream and is not evidence that the generic GSI works.

## 8. Immediate next actions

- [x] Confirm the exact lunch combo from AOSP GSI documentation and the LineageOS `lineage-24.0` product definition.
- [ ] Produce and inspect the unmodified `gsi_arm64` baseline.
- [x] Add the baseline build helper with source-tree, host-resource, lunch-target and artifact checks.
- [ ] Integrate RichardOS changes incrementally.
- [ ] Publish the first artifact only after the release gate is met.
