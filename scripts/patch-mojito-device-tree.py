#!/usr/bin/env python3
"""Preserve both common and Qualcomm SM6150 vendor VINTF manifests."""
from pathlib import Path

TARGET = Path("device/xiaomi/sm6150-common/BoardConfigCommon.mk")
BROKEN = """DEVICE_MANIFEST_FILE += hardware/qcom-caf/sm8150/media/conf_files/sm6150/c2_manifest_vendor.xml
DEVICE_MATRIX_FILE := hardware/qcom-caf/common/compatibility_matrix.xml
DEVICE_MANIFEST_FILE := $(COMMON_PATH)/configs/manifests/manifest.xml"""
FIXED = """DEVICE_MANIFEST_FILE := $(COMMON_PATH)/configs/manifests/manifest.xml
DEVICE_MANIFEST_FILE += hardware/qcom-caf/sm8150/media/conf_files/sm6150/c2_manifest_vendor.xml
DEVICE_MATRIX_FILE := hardware/qcom-caf/common/compatibility_matrix.xml"""


def main() -> int:
    if not TARGET.is_file():
        raise SystemExit(f"ERROR: expected device tree file not found: {TARGET}")

    content = TARGET.read_text(encoding="utf-8")
    broken_count = content.count(BROKEN)
    fixed_count = content.count(FIXED)

    if broken_count == 1 and fixed_count == 0:
        TARGET.write_text(content.replace(BROKEN, FIXED, 1), encoding="utf-8")
        print("Applied SM6150 C2 vendor manifest ordering fix.")
    elif broken_count == 0 and fixed_count == 1:
        print("SM6150 C2 vendor manifest ordering is already fixed.")
    else:
        raise SystemExit(
            "ERROR: BoardConfigCommon.mk does not match the expected source "
            "or contains ambiguous manifest declarations; refusing to patch."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
