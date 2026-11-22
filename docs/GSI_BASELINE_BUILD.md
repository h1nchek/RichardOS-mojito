# Building the clean universal GSI baseline

This runbook builds an **unmodified LineageOS ARM64 GSI** first. It does not build the `mojito` port and does not apply RichardOS patches.

## Source requirements

Use a dedicated Linux x86_64 build host and a fully synced LineageOS `lineage-24.0` source tree. The current project recommendation is at least 8 CPU threads, 28 GiB RAM and 300 GiB free disk; 16 CPU threads, 64 GiB RAM and 500 GiB NVMe are preferred. These are project planning thresholds, not guarantees that every build will fit.

Initialize the source tree using the official LineageOS manifest:

```bash
mkdir -p "$HOME/android/richardos-gsi"
cd "$HOME/android/richardos-gsi"
repo init -u https://github.com/LineageOS/android.git -b lineage-24.0 --git-lfs --no-clone-bundle
repo sync -j4 --fail-fast
```

The synced tree must contain `.repo/`, `build/envsetup.sh`, `device/generic/common/AndroidProducts.mk` and `device/generic/common/gsi_arm64.mk`.

The project has verified upstream that `AndroidProducts.mk` registers `gsi_arm64.mk` and that the makefile declares product `gsi_arm64` and device `generic_arm64`. AOSP documents `gsi_arm64-userdebug` as the standard ARM64 GSI build target. The helper still validates the resolved product, device and variant against the actual synced checkout before compiling.

## Run the baseline builder

Clone RichardOS separately, then run:

```bash
git clone https://github.com/h1nchek/RichardOS-mojito.git
cd RichardOS-mojito
git checkout gsi/0.9.0-expansion
ANDROID_BUILD_TOP="$HOME/android/richardos-gsi" JOBS=8 \
  bash scripts/build-gsi-baseline.sh
```

The helper checks the source tree, product registration and host resources; runs the candidate `gsi_arm64-userdebug` lunch selection; verifies `TARGET_PRODUCT`, `TARGET_DEVICE` and `TARGET_BUILD_VARIANT`; builds `systemimage` without RichardOS patches; and saves `system.img`, its SHA-256 checksum and a resolved repo manifest.

If lunch cannot resolve to the expected product/device/variant, the script stops. Do not bypass that check by forcing different variables; inspect the actual synced product definitions and update the documented target deliberately.

## Optional GitHub Actions workflow

`.github/workflows/build-gsi-baseline.yml` is a manual workflow for a dedicated self-hosted runner. It expects runner labels `self-hosted`, `linux`, `x64`, `android-build`, the repository Actions variable `ANDROID_BUILD_TOP` containing the absolute path to the pre-synced source tree, and optional `ANDROID_BUILD_JOBS` for parallel jobs.

Do not register an ordinary desktop or a low-memory VPS as the Android build runner. GitHub-hosted runners are not used for this full Android compile. The workflow is not ready to run until a suitable runner and source checkout are provisioned.

## What this proves — and what it does not

A successful job proves that the unmodified upstream product compiled into an image in that source environment. It does **not** prove RichardOS customizations compile, that the image boots, or that any particular Treble phone is compatible. Those are separate gates.

The next stage is to integrate RichardOS features incrementally on a separate build path, then arrange controlled compatibility testing on non-primary test devices with a reviewed recovery plan.