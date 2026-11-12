# First compilation: Redmi Note 10 (mojito)

This is the first-build runbook. It intentionally separates the initial LineageOS baseline from RichardOS customizations so that device bring-up failures are not confused with branding or Settings changes.

## Required build host

Use a native or virtualized **Linux x86_64** environment, not Windows Command Prompt or PowerShell.

Recommended minimum for this source set:

- 32 GB RAM.
- 350 GB free SSD before syncing; keep additional room for build output and caches.
- Stable internet connection.
- A filesystem with enough free inodes.
- Android `repo`, Git, Python 3, Java/build dependencies required by the target LineageOS branch.

The build helper caps parallel compilation at 8 jobs by default. Override with `JOBS=4` or another value from 1 to 8 if memory is constrained.

## 1. Initialize the Android source tree

Choose a dedicated directory with sufficient free space. The commands below do not format disks or delete existing files.

```bash
mkdir -p "$HOME/android/richardos-mojito"
cd "$HOME/android/richardos-mojito"
repo init -u https://github.com/LineageOS/android.git -b lineage-24.0 --git-lfs --no-clone-bundle
mkdir -p .repo/local_manifests
cp /path/to/RichardOS-mojito/manifests/mojito-lineage24.xml \
  .repo/local_manifests/richardos-mojito.xml
repo sync -j4 --fail-fast
```

Replace `/path/to/RichardOS-mojito` with the actual clone location. Do not run `repo sync` until the host has enough free SSD space and a stable connection.

## 2. Run the baseline build

From the RichardOS project checkout:

```bash
JOBS=4 bash scripts/build-baseline.sh "$HOME/android/richardos-mojito"
```

The script verifies the host and source-tree prerequisites, runs the repository's unit tests, compares every local `extend-project` against the synced LineageOS `default.xml` and `snippets/lineage.xml`, checks required Qualcomm/Lineage policy and hardware source directories, records the resolved manifest, applies the narrowly guarded SM6150 VINTF ordering correction, checks vendor source paths and VINTF XML, then builds the LineageOS baseline with `breakfast mojito` and `m bacon`.

The baseline script deliberately does **not** apply RichardOS branding, wallpapers, boot animation, or the experimental Settings patch. First establish that the device sources can produce a baseline package. The separate `scripts/build.sh` is the RichardOS customization/build stage and applies the Settings patch.

## 3. After a successful baseline

1. Save the resolved manifest and package SHA-256.
2. Review the build log and output package metadata.
3. Do not flash until the exact target, package integrity, backup, recovery compatibility, and installation procedure have been reviewed.
4. Arrange a controlled boot test and record hardware behavior.
5. Only after the baseline is known-good, run `bash scripts/build.sh "$HOME/android/richardos-mojito"` from the RichardOS checkout. This second-stage script installs the RichardOS branding and wallpapers, applies the native Settings Hub patch, and builds the customized ROM.

## Current limitations

The source manifest pins candidate device, kernel, vendor, and Qualcomm legacy-UM policy repositories. CI verifies the names and paths of upstream manifest extensions, and verifies that the pinned project revisions exist. Static CI checks do not prove that those revisions are mutually build-compatible. The first full compile is the test that will reveal missing dependencies, Soong/Make errors, compiler incompatibilities, or device-tree issues.

No successful full build, installable RichardOS package, or physical-device boot test is currently claimed. Keep proprietary vendor files and signing keys private; do not commit credentials or private signing material.
