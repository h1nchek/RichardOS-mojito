import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "audit-vendor-blobs.py"
SPEC = importlib.util.spec_from_file_location("vendor_blob_audit", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class CollectEntriesTests(unittest.TestCase):
    def test_multiline_product_copy_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            makefile = Path(tmp) / "vendor.mk"
            makefile.write_text(
                "PRODUCT_COPY_FILES += \\\n"
                "    vendor/xiaomi/device/proprietary/a.bin:$(TARGET_COPY_OUT_VENDOR)/a.bin \\\n"
                "    vendor/xiaomi/device/proprietary/b.bin:$(TARGET_COPY_OUT_VENDOR)/b.bin\n"
            )
            self.assertEqual(
                MODULE.collect_entries(makefile),
                [
                    "vendor/xiaomi/device/proprietary/a.bin",
                    "vendor/xiaomi/device/proprietary/b.bin",
                ],
            )

    def test_inline_assignment_and_ignores_other_variables(self):
        with tempfile.TemporaryDirectory() as tmp:
            makefile = Path(tmp) / "vendor.mk"
            makefile.write_text(
                "PRODUCT_PACKAGES += some-service\n"
                "PRODUCT_COPY_FILES += vendor/a.bin:vendor/a.bin\n"
            )
            self.assertEqual(MODULE.collect_entries(makefile), ["vendor/a.bin"])


    def test_unresolved_source_path_returns_incomplete_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            makefile = root / "vendor.mk"
            makefile.write_text(
                "PRODUCT_COPY_FILES += $(LOCAL_PATH)/blob.bin:vendor/blob.bin\\n"
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    str(root),
                    "--makefile",
                    "vendor.mk",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("Unresolved variable paths: 1", result.stdout)


if __name__ == "__main__":
    unittest.main()
