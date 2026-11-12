# RichardOS branding layer

This directory contains RichardOS-owned product branding, kept separate from
upstream LineageOS files.

## Integration

Include `vendor/richardos/config/branding.mk` from the final
`device/xiaomi/mojito` product makefile, after the LineageOS product
configuration has been included:

```make
$(call inherit-product, vendor/richardos/config/branding.mk)
```

The exact product makefile and include order must be checked in the synced
mojito device tree before applying this integration.

## Properties

- Android product brand: `RichardOS`
- Product name: `RichardOS_mojito`
- Model: `Xiaomi Redmi Note 10`
- RichardOS version: `1.0` (initial branding placeholder)
- Device identifier: `mojito`
- Build type: `UNOFFICIAL`

The Android platform version, build ID, security patch level, signing keys,
and verified-boot configuration remain owned by the platform build system.
This branding layer does not claim a successful build or boot test.
