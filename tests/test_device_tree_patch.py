import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "patch-mojito-device-tree.py"


class DeviceTreePatchTests(unittest.TestCase):
    def run_patch(self, root: Path):
        return subprocess.run(
            [sys.executable, str(SCRIPT)],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )

    def prepare_tree(self, root: Path, content: str) -> Path:
        target = root / "device/xiaomi/sm6150-common/BoardConfigCommon.mk"
        target.parent.mkdir(parents=True)
        target.write_text(content, encoding="utf-8")
        return target

    def test_reorders_manifest_assignment(self):
        broken = (
            "prefix\n"
            "DEVICE_MANIFEST_FILE += hardware/qcom-caf/sm8150/media/conf_files/sm6150/c2_manifest_vendor.xml\n"
            "DEVICE_MATRIX_FILE := hardware/qcom-caf/common/compatibility_matrix.xml\n"
            "DEVICE_MANIFEST_FILE := $(COMMON_PATH)/configs/manifests/manifest.xml\n"
            "suffix\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            target = self.prepare_tree(Path(tmp), broken)
            result = self.run_patch(Path(tmp))
            self.assertEqual(result.returncode, 0, result.stderr)
            output = target.read_text(encoding="utf-8")
            self.assertLess(
                output.index("DEVICE_MANIFEST_FILE := $(COMMON_PATH)"),
                output.index("DEVICE_MANIFEST_FILE += hardware/qcom-caf"),
            )
            self.assertIn("prefix\n", output)
            self.assertIn("suffix\n", output)

    def test_is_idempotent(self):
        fixed = (
            "DEVICE_MANIFEST_FILE := $(COMMON_PATH)/configs/manifests/manifest.xml\n"
            "DEVICE_MANIFEST_FILE += hardware/qcom-caf/sm8150/media/conf_files/sm6150/c2_manifest_vendor.xml\n"
            "DEVICE_MATRIX_FILE := hardware/qcom-caf/common/compatibility_matrix.xml"
        )
        with tempfile.TemporaryDirectory() as tmp:
            target = self.prepare_tree(Path(tmp), fixed)
            result = self.run_patch(Path(tmp))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(target.read_text(encoding="utf-8"), fixed)

    def test_refuses_unrecognized_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = self.prepare_tree(Path(tmp), "DEVICE_MANIFEST_FILE := something_else\n")
            result = self.run_patch(Path(tmp))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("refusing to patch", result.stderr)
            self.assertEqual(
                target.read_text(encoding="utf-8"), "DEVICE_MANIFEST_FILE := something_else\n"
            )


if __name__ == "__main__":
    unittest.main()
