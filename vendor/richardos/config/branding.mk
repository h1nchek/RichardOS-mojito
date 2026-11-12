#
# RichardOS product identity and system properties.
# Included at the end of the mojito product makefile; never changes PRODUCT_NAME.
#

RICHARDOS_VERSION_MAJOR := 1
RICHARDOS_VERSION_MINOR := 0
RICHARDOS_VERSION := $(RICHARDOS_VERSION_MAJOR).$(RICHARDOS_VERSION_MINOR)

PRODUCT_BRAND := RichardOS
PRODUCT_MODEL := Redmi Note 10
PRODUCT_MANUFACTURER := Xiaomi

PRODUCT_SYSTEM_PROPERTIES += \
    ro.richardos.device=mojito \
    ro.richardos.version=$(RICHARDOS_VERSION) \
    ro.richardos.codename=RichardOS \
    ro.richardos.build_type=UNOFFICIAL \
    ro.richardos.maintainer=h1nchek
