# RichardOS Hub integration

The app module lives at `packages/apps/RichardOSHub`.

After the repository is synced into a compatible Android source tree, add the module to the mojito product package list:

```make
PRODUCT_PACKAGES += \
    RichardOSHub
```

Do not paste this into the meta-repository: it is a source repository, not a complete Android device tree. Apply the line to the actual product makefile used by the mojito build.

## Before building

1. Confirm the platform branch and all device/vendor/kernel revisions are mutually compatible.
2. Confirm that the target product includes `system_ext` and supports privileged apps there.
3. Run Soong/Android build and fix compile or policy errors.
4. Review privileged-permission requirements before adding any privileged permissions. The initial app intentionally requests none.
5. Install on a test device and verify launch, palette persistence, rotation, dark mode, and navigation.

## Current limitations

The first version is a UI and preference-storage foundation. It does not yet modify framework Monet resources, SystemUI, lock screen, root state, or device security settings. A successful app build would not by itself mean a bootable RichardOS ROM.
