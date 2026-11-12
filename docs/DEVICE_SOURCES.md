# Redmi Note 10 (mojito) — source audit

Checked on 2026-11-09. Source-level validation only; no successful build or boot test has been recorded.

## Candidate device source set

All five repositories expose branch `17.0`. Their exact commit IDs were resolved from those refs and pinned in `manifests/mojito-lineage24.xml` on 2026-11-09:

| Build path | Repository | Pinned revision | Verification |
|---|---|---|---|
| `device/xiaomi/mojito` | [device_xiaomi_mojito](https://github.com/ximi-mojito/device_xiaomi_mojito) | `efdf9962669b` | Product, device and board makefiles inspected |
| `device/xiaomi/sm6150-common` | [device_xiaomi_sm6150-common](https://github.com/ximi-mojito/device_xiaomi_sm6150-common) | `aae2067ea624` | Common board and product makefiles inspected |
| `kernel/xiaomi/mojito` | [android_kernel_xiaomi_mojito](https://github.com/ximi-mojito/android_kernel_xiaomi_mojito) | `87e3f1844a65` | `mojito_defconfig` and kernel baseline inspected |
| `vendor/xiaomi/mojito` | [android_vendor_xiaomi_mojito](https://github.com/ximi-mojito/android_vendor_xiaomi_mojito) | `ef30fe68e01b` | Device vendor makefile and blob source paths inspected |
| `vendor/xiaomi/sm6150-common` | [android_vendor_xiaomi_sm6150-common](https://github.com/ximi-mojito/android_vendor_xiaomi_sm6150-common) | `b6f3a74a9288` | Common vendor makefile and blob source paths inspected |

## Verified makefile relationships

- `AndroidProducts.mk` registers `lineage_mojito.mk`.
- `lineage_mojito.mk` defines `lineage_mojito`, device `mojito`, model `Redmi Note 10`, and inherits LineageOS common phone configuration.
- `device.mk` inherits `device/xiaomi/sm6150-common/sm6150.mk` and `vendor/xiaomi/mojito/mojito-vendor.mk`.
- `device.mk` optionally inherits Leica camera and MIUI-app vendor configs if those directories exist.
- `BoardConfig.mk` selects `kernel/xiaomi/mojito` and `mojito_defconfig`, asserts `mojito,sunny`, and includes common and device vendor board configs.
- `BoardConfigCommon.mk` includes `vendor/xiaomi/sm6150-common/BoardConfigVendor.mk`.
- `sm6150.mk` inherits `vendor/xiaomi/sm6150-common/sm6150-common-vendor.mk` and references Qualcomm CAF common and SM8150 audio projects.
- The generated vendor makefiles contain **455 unique concrete `PRODUCT_COPY_FILES` source references**: 348 in `mojito-vendor.mk` and 107 in `sm6150-common-vendor.mk`. On 2026-11-06, both vendor repositories' complete recursive Git trees were fetched from branch `17.0` and every reference was matched against its corresponding `proprietary/` path: **455/455 present, 0 missing**. The GitHub trees were not truncated (622 device-vendor files and 602 common-vendor files). This is a source-tree presence check, not a local post-`repo sync` audit; it does not validate blob contents, checksums against the original firmware, ABI/linker compatibility, licensing, VINTF, or runtime behavior. The local `scripts/audit-vendor-blobs.py` remains useful to repeat the source-path check inside the actual synced Android workspace.

## SM6150 VINTF manifest ordering fix

The current `17.0` common device tree assigns the common manifest after appending the Qualcomm SM6150 Codec2 vendor manifest. Because `:=` replaces the variable, the Qualcomm manifest would be dropped. `scripts/patch-mojito-device-tree.py` now applies a guarded, idempotent reorder immediately after `repo sync` in `scripts/build.sh`. It changes only the exact known three-line sequence and aborts if the source differs or is ambiguous. Three unit tests cover the transformation, idempotence, and refusal of an unknown source. This has not yet been run against a complete synced Android checkout.

## BlueOS patch integration

Upstream `vendorsetup.sh` runs `scripts/apply-patches.sh` when `build/envsetup.sh` is sourced. The patch script exits nonzero if any patch fails, so the build script's `set -e` should stop at that stage rather than silently producing a non-BlueOS build.

Upstream `manifests/blueos-pinned.xml` currently contains 12 `extend-project` entries with empty `name` values. That is not a usable project selector. This repository carries a corrected local fallback at `manifests/blueos-pinned.xml`. Its 12 revisions have now been matched to their actual LineageOS project paths by resolving the commit SHAs against the corresponding GitHub project repositories. The earlier draft had several revisions assigned to the wrong paths; the mapping has been corrected. The manifest still needs an actual `repo sync` test in a complete LineageOS checkout before it can be treated as build-validated. Use it only if fresh-branch patch application fails.

## Manifest coverage and unresolved dependencies

The local device manifest declares the five device/common/kernel/vendor repositories plus the separate LineageOS `hardware/xiaomi` project. It also promotes Google and Qualcomm projects required by the device and vendor trees into the `default` sync group. This matters because the LineageOS 24.0 manifest places several of these projects in device-family groups (for example `qcom`, `msmnile`, and `kaanapali-vendor`), which are not guaranteed to be selected by an ordinary default `repo sync`.

The required group promotions currently cover:

- `hardware/google/interfaces` and `hardware/google/pixel`;
- `hardware/qcom-caf/bootctrl`, `common`, `sm8150/audio`, `sm8150/display`, `sm8150/media`, and `wlan`;
- `vendor/qcom/opensource/dataservices`, `commonsys-intf/display`, `display`, `interfaces`, and `usb`.

The optional Leica/MIUI trees are guarded by `inherit-product-if-exists` and are not declared by this port manifest.

This closes a manifest-selection gap found during the November 9 audit; it does not prove that every module compiles or that all proprietary files and firmware are compatible. A clean sync, dependency checks, and product build are still required.

## Compatibility

Upstream BlueOS targets LineageOS 24.0 / Android 17. Its main development device is Pixel 6a; that does not establish support for mojito. Device branch `17.0` is a plausible Android 17 target, but its name alone does not prove compatibility with the exact LineageOS platform manifest. Every BlueOS patch must apply on the synced revisions.

### Soong namespace and vendor module cross-check

The `17.0` vendor/device `Android.bp` files were inspected directly:

- Device vendor namespace imports: `hardware/qcom-caf/sm8150`, `hardware/xiaomi`, `vendor/qcom/opensource/display`, and `vendor/xiaomi/sm6150-common`.
- Common vendor namespace imports: `device/xiaomi/sm6150-common`, `hardware/qcom-caf/sm8150`, `hardware/qcom-caf/wlan`, `hardware/xiaomi`, `vendor/qcom/opensource/dataservices`, and `vendor/qcom/opensource/display`.
- Common device namespace imports: `hardware/xiaomi`, `hardware/google/interfaces`, `hardware/google/pixel/pixelstats`, `hardware/google/pixel/power-libperfmgr`, `hardware/qcom-caf/common/libqti-perfd-client`, and `hardware/lineage/interfaces/power-libperfmgr`.

The proprietary vendor `Android.bp` files contain many prebuilt shared libraries, and dependency arrays also occur under architecture-specific `target` blocks. The Soong preflight tool therefore collects literal dependency arrays at nested property depth as well as module-level properties. It still cannot resolve the imported namespaces or determine whether every dependency is available in the exact synced LineageOS revision.

## Local manifests

- [mojito-lineage24.xml](../manifests/mojito-lineage24.xml): five device-side repositories.
- [blueos.xml](../manifests/blueos.xml): upstream BlueOS.
- [blueos-pinned.xml](../manifests/blueos-pinned.xml): corrected fallback pins for BlueOS 0.8.1 patch projects.

## Release blockers

1. Validate the corrected fallback manifest with `repo sync` if it is needed.
2. Complete a full comparison of every `PRODUCT_COPY_FILES`/Soong prebuilt reference against the committed proprietary tree, then verify firmware compatibility.
3. Confirm all five `17.0` repositories build against LineageOS 24.0.
4. Run a clean full build and inspect the ZIP and SHA-256.
5. Boot-test the exact hardware and validate radio, Wi-Fi, Bluetooth, camera, audio, sensors, fingerprint, charging, encryption and OTA.

No release ZIP, boot image or recovery image is produced by this repository yet. Do not commit private signing keys or firmware images.


### LineageOS 24.0 / Qualcomm CAF dependency cross-check

The device and common trees do not contain `lineage.dependencies`; their external build dependencies are declared through Soong namespace imports, product makefiles, and BoardConfig references. Cross-checking those paths against the LineageOS 24.0 manifest snippet confirms that the standard source manifest supplies the relevant projects:

- `hardware/google/interfaces`, `hardware/google/pixel`, and `hardware/lineage/interfaces` are standard LineageOS projects.
- `hardware/qcom-caf/common` supplies the common CAF namespace, including the `libqti-perfd-client` subdirectory, and the common manifest linkfiles.
- `hardware/qcom-caf/sm8150/audio`, `display`, and `media` are declared against the `lineage-24.0-caf-sm8150` branches.
- `hardware/qcom-caf/wlan` is declared by the LineageOS manifest on its CAF branch.

The corresponding LineageOS repositories expose the expected `lineage-24.0` / `lineage-24.0-caf-sm8150` branches. This confirms the manifest-level project mapping, not successful compilation or compatibility of every module. The common tree's references to SM8150 audio configuration files and the SM6150 C2 manifest still need to be tested in an actual sync/build.


## VINTF XML preflight utility

A repository-side XML preflight helper is available:

```bash
python3 scripts/audit-vintf.py path/to/manifest.xml path/to/compatibility_matrix.xml
```

It verifies XML well-formedness, accepted VINTF root tags, non-empty HAL names/FQNames, and duplicate exact HAL instance declarations inside each input file. It is intentionally conservative: duplicate declarations across separate files, framework/vendor matching, target-level compatibility, service registration, and runtime behavior require the Android build tools (especially `checkvintf`) in a complete synced tree.


## Soong module source preflight

`scripts/audit-soong-deps.py` indexes named module blocks in explicitly supplied `Android.bp` files and compares literal module names referenced by common dependency properties. Example:

```bash
python3 scripts/audit-soong-deps.py --strict \
  vendor/xiaomi/mojito/Android.bp \
  vendor/xiaomi/sm6150-common/Android.bp \
  vendor/qcom/opensource/display/Android.bp
```

The default mode reports dependencies not found in the supplied file set without treating them as build failures. `--strict` returns 1 for any such unindexed dependency. Because Soong namespaces and project-wide module visibility affect resolution, an unindexed name is not necessarily missing. The parser now rejects unterminated module blocks as malformed input (exit status 2), preventing a partial index from appearing successful. This script does not parse the full Blueprint language and cannot replace Soong's actual dependency graph or a successful product build.


## Local repo manifest structural audit

Run `python3 scripts/audit_repo_manifests.py manifests/*.xml` before syncing. The check detects duplicate project paths, missing revisions, undeclared remotes, and malformed `extend-project` entries. It does not check whether remote URLs or revisions are reachable; `repo sync` is still the source of truth.


## Live branch resolution snapshot (2026-11-06)

The GitHub branch API was queried for every repository referenced by `manifests/mojito-lineage24.xml`. All five remote `17.0` refs resolve successfully at the time of this check:

| Repository | Resolved commit | Committer date | Commit subject |
|---|---|---|---|
| `device_xiaomi_mojito` | `efdf9962669b2f0dec80906e892a9b8d98dbe09b` | 2026-10-15 | Stop shipping 32-bit Zygote |
| `device_xiaomi_sm6150-common` | `aae2067ea624cf86c10df3633725260920a19c87` | 2026-10-16 | Enable charging control bypass mode |
| `android_kernel_xiaomi_mojito` | `87e3f1844a65ef9a1cb965fac6096a7dcd84f6ea` | 2026-10-23 | Hardcode compiler optimizations for sd678 |
| `android_vendor_xiaomi_mojito` | `ef30fe68e01b50088093b56da82457202ab1dfe3` | 2026-02-08 | Patch libtinyxml2 to libtinyxml2-v34 |
| `android_vendor_xiaomi_sm6150-common` | `b6f3a74a92888bb8f0f52144d89488ad6fa3fd54` | 2026-02-08 | Patch libtinyxml2 to libtinyxml2-v34 |

This closes the narrow question of whether the five manifest branch names currently exist. It does **not** validate their cross-repository compatibility, prove that the revisions build together, or replace a successful `repo sync` and product build. The manifest intentionally tracks branch `17.0`, so future syncs may resolve to newer commits.


## Complete vendor source-path snapshot (2026-11-06)

The `17.0` recursive Git trees were compared with every concrete `PRODUCT_COPY_FILES` source path in the generated vendor makefiles. All paths map beneath the corresponding repository's `proprietary/` directory.

| Vendor tree | Makefile references | Files in Git tree | Matched | Missing |
|---|---:|---:|---:|---:|
| `android_vendor_xiaomi_mojito` | 348 | 622 | 348 | 0 |
| `android_vendor_xiaomi_sm6150-common` | 107 | 602 | 107 | 0 |
| **Total** | **455** | **1,224** | **455** | **0** |

This closes the static file-presence audit for the current GitHub `17.0` snapshots. Re-run it after vendor branch updates and repeat `scripts/audit-vendor-blobs.py` after `repo sync`; the actual Android build remains authoritative.
