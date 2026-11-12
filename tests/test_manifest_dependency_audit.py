import pathlib
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from audit_manifest_dependencies import audit


class ManifestDependencyAuditTests(unittest.TestCase):
    def test_detects_missing_qualcomm_policy_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            local = root / "local.xml"
            upstream = root / "upstream.xml"
            local.write_text(
                '<manifest>'
                '<project name="android_device_qcom_sepolicy" path="device/qcom/sepolicy"/>'
                '</manifest>',
                encoding="utf-8",
            )
            upstream.write_text(
                '<manifest>'
                '<project name="LineageOS/android_packages_apps_Settings" path="packages/apps/Settings"/>'
                '</manifest>',
                encoding="utf-8",
            )
            errors = audit(local, [upstream])
            self.assertTrue(any("device/qcom/sepolicy_vndr" in error for error in errors))
            self.assertTrue(any("device/qcom/sepolicy" in error for error in errors))

    def test_rejects_unknown_extend_project_name_or_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            local = root / "local.xml"
            upstream = root / "upstream.xml"
            local.write_text(
                '<manifest><extend-project name="LineageOS/android_wrong" '
                'path="hardware/wrong"/></manifest>',
                encoding="utf-8",
            )
            upstream.write_text(
                '<manifest><project name="LineageOS/android_right" '
                'path="hardware/right"/></manifest>',
                encoding="utf-8",
            )
            errors = audit(local, [upstream])
            self.assertTrue(any("does not match" in error for error in errors))

    def test_real_local_extensions_are_declared_in_upstream_manifest(self):
        errors = audit(
            ROOT / "manifests/mojito-lineage24.xml",
            [
                ROOT / "tests/fixtures/lineage-default-min.xml",
                ROOT / "tests/fixtures/lineage-snippet-min.xml",
            ],
        )
        self.assertEqual([], errors)


if __name__ == "__main__":
    unittest.main()
