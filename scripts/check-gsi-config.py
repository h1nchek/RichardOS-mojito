#!/usr/bin/env python3
"""Validate RichardOS GSI target metadata without building or modifying devices."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "gsi" / "targets.json"


def main() -> int:
    data = json.loads(CONFIG.read_text(encoding="utf-8"))
    assert data["schema_version"] == 1
    assert data["status"] == "preparation"
    assert data["platform"]["name"] == "LineageOS"
    assert data["platform"]["branch"] == "lineage-24.0"
    target = data["target"]
    assert target["name"] == "gsi_arm64"
    assert target["product_definition"] == "device/generic/common/gsi_arm64.mk"
    assert target["architecture"] == "arm64"
    assert target["binder_bitness"] == 64
    assert target["variant"] == "userdebug"
    assert target["lunch_alias"] == "unverified"
    assert data["device_specific"] is False
    assert data["image_built"] is False
    assert data["device_tested"] is False
    print("GSI metadata is valid; build and device testing remain unclaimed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
