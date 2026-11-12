# Redmi Note 10 (mojito) — device source notes

Last reviewed: 2026-11-09. These are source-level observations only. No successful full build or physical-device boot test is recorded.

## Candidate source set

The local manifest pins these candidate repositories to immutable revisions resolved from branch `17.0`:

| Build path | Repository | Pinned revision |
|---|---|---|
| `device/xiaomi/mojito` | [device_xiaomi_mojito](https://github.com/ximi-mojito/device_xiaomi_mojito) | `efdf9962669b` |
| `device/xiaomi/sm6150-common` | [device_xiaomi_sm6150-common](https://github.com/ximi-mojito/device_xiaomi_sm6150-common) | `aae2067ea624` |
| `kernel/xiaomi/mojito` | [android_kernel_xiaomi_mojito](https://github.com/ximi-mojito/android_kernel_xiaomi_mojito) | `87e3f1844a65` |
| `vendor/xiaomi/mojito` | [android_vendor_xiaomi_mojito](https://github.com/ximi-mojito/android_vendor_xiaomi_mojito) | `ef30fe68e01b` |
| `vendor/xiaomi/sm6150-common` | [android_vendor_xiaomi_sm6150-common](https://github.com/ximi-mojito/android_vendor_xiaomi_sm6150-common) | `b6f3a74a9288` |

The manifest also selects LineageOS Xiaomi hardware and Google/Qualcomm dependencies needed by the device trees.

## Makefile relationships reviewed

- `AndroidProducts.mk` registers `lineage_mojito.mk`.
- `lineage_mojito.mk` defines the `mojito` product and Redmi Note 10 model.
- `device.mk` inherits the SM6150 common configuration and device vendor makefile.
- `BoardConfig.mk` selects the mojito kernel and `mojito_defconfig`.
- The common device tree inherits the common vendor configuration and Qualcomm CAF components.

The reviewed vendor makefiles referenced 455 concrete `PRODUCT_COPY_FILES` source paths. Those paths were matched against the corresponding upstream proprietary source trees during the earlier audit. This is only a file-presence check; it does not validate binary contents, checksums, ABI compatibility, firmware compatibility, licensing, VINTF, or runtime behavior. Repeat the local audit after a fresh `repo sync`.

## VINTF ordering correction

The common device tree contained a known ordering issue involving the common manifest and Qualcomm SM6150 Codec2 vendor manifest. `scripts/patch-mojito-device-tree.py` applies a guarded, idempotent correction for the exact reviewed source sequence and aborts if the source differs or is ambiguous. Unit tests cover the expected transformation, idempotence, and refusal of an unknown source. It has not yet been tested against a complete fresh checkout.

## Soong dependency notes

The reviewed device/common/vendor `Android.bp` files import namespaces under `hardware/xiaomi`, `hardware/google`, `hardware/qcom-caf`, `hardware/lineage`, and `vendor/qcom/opensource`. The included Soong audit helper can index literal dependency declarations in selected files, but it cannot evaluate Blueprint expressions, resolve all namespaces, or replace the real Soong build.

## Platform compatibility

The device repositories' `17.0` branch names are not proof of compatibility with a particular LineageOS manifest revision. The current build helper targets LineageOS 24.0. The first milestone is a clean baseline build; if the pinned source set is incompatible, update and re-audit the manifest before attempting RichardOS customizations.

## Required validation

1. Complete a fresh `repo sync` using the local manifest.
2. Run vendor blob, VINTF, and Soong dependency audits against the actual checkout.
3. Complete a clean full LineageOS baseline build.
4. Inspect the generated package and verify its SHA-256.
5. Boot-test on a physical Redmi Note 10 and validate radio, Wi-Fi, Bluetooth, camera, audio, sensors, fingerprint, charging, encryption, and OTA behavior.

No release ZIP, boot image, or recovery image is available yet. Do not commit private signing keys or proprietary firmware images.
