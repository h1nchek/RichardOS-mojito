#
# RichardOS product branding
# Include from the mojito product makefile after the LineageOS product config.
#

RICHARDOS_VERSION_MAJOR := 1
RICHARDOS_VERSION_MINOR := 0
RICHARDOS_VERSION := $(RICHARDOS_VERSION_MAJOR).$(RICHARDOS_VERSION_MINOR)

PRODUCT_BRAND := RichardOS
PRODUCT_NAME := RichardOS_mojito
PRODUCT_MODEL := Xiaomi Redmi Note 10
PRODUCT_MANUFACTURER := Xiaomi

PRODUCT_SYSTEM_PROPERTIES += \
    ro.richardos.device=mojito \
    ro.richardos.version=$(RICHARDOS_VERSION) \
    ro.richardos.codename=RichardOS \
    ro.richardos.build_type=UNOFFICIAL

# Keep the Android platform release and security patch level controlled by
# the LineageOS build system. Do not override them with branding values.
