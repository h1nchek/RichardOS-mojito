#!/usr/bin/env python3
"""Validate RichardOS GSI metadata and, when supplied, its upstream product definition."""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "gsi" / "targets.json"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("upstream_product", nargs="?", type=Path)
    args = parser.parse_args()

    try:
        data = json.loads(CONFIG.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot read GSI metadata: {exc}", file=sys.stderr)
        return 2

    checks = [
        (data.get("schema_version") == 1, "unsupported schema_version"),
        (data.get("status") == "preparation", "GSI status must remain preparation until a build is verified"),
        (data.get("platform", {}).get("name") == "LineageOS", "unexpected platform"),
        (data.get("platform", {}).get("branch") == "lineage-24.0", "unexpected platform branch"),
    ]
    target = data.get("target", {})
    checks.extend([
        (target.get("name") == "gsi_arm64", "unexpected GSI product name"),
        (target.get("product_definition") == "device/generic/common/gsi_arm64.mk", "unexpected product definition path"),
        (target.get("architecture") == "arm64", "GSI architecture must be arm64"),
        (target.get("binder_bitness") == 64, "GSI binder bitness must be 64"),
        (target.get("variant") == "userdebug", "GSI build variant must remain userdebug"),
        (target.get("lunch_alias") == "unverified", "do not claim an unverified lunch alias"),
        (data.get("device_specific") is False, "generic GSI must not include device-specific configuration"),
        (data.get("image_built") is False, "metadata must not claim an image was built"),
        (data.get("device_tested") is False, "metadata must not claim device testing"),
    ])
    errors = [message for passed, message in checks if not passed]

    if args.upstream_product:
        try:
            product = args.upstream_product.read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"cannot read upstream product definition: {exc}")
        else:
            for expression, message in [
                (r"(?m)^PRODUCT_NAME\s*:=\s*gsi_arm64\s*$", "upstream PRODUCT_NAME is not gsi_arm64"),
                (r"(?m)^PRODUCT_DEVICE\s*:=\s*generic_arm64\s*$", "upstream PRODUCT_DEVICE is not generic_arm64"),
                (r"core_64_bit\.mk", "upstream product does not inherit core_64_bit.mk"),
                (r"generic_system\.mk", "upstream product does not inherit generic_system.mk"),
                (r"gsi_system_ext\.mk", "upstream product does not inherit gsi_system_ext.mk"),
                (r"gsi_product\.mk", "upstream product does not inherit gsi_product.mk"),
                (r"gsi_release\.mk", "upstream product does not inherit gsi_release.mk"),
                (r"(?m)^PRODUCT_SOONG_DEFINED_SYSTEM_IMAGE\s*:=\s*android_gsi\s*$", "upstream system image definition is not android_gsi"),
                (r"(?m)^USE_SOONG_DEFINED_SYSTEM_IMAGE\s*:=\s*true\s*$", "upstream product does not enable the Soong-defined system image"),
            ]:
                if not re.search(expression, product):
                    errors.append(message)

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    suffix = " and upstream product definition" if args.upstream_product else ""
    print(f"GSI metadata{suffix} valid; build and device testing remain unclaimed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
