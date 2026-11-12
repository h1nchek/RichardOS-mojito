import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "audit-vintf.py"
SPEC = importlib.util.spec_from_file_location("vintf_audit", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class VintfAuditTests(unittest.TestCase):
    def test_valid_manifest_and_hal_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "manifest.xml"
            path.write_text(
                '<manifest version="2.0"><hal format="hidl">'
                '<name>android.hardware.foo</name>'
                '<fqname>@1.0::IFoo/default</fqname>'
                '</hal></manifest>'
            )
            errors, count = MODULE.audit(path)
            self.assertEqual(errors, [])
            self.assertEqual(count, 1)

    def test_duplicate_instance_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "manifest.xml"
            path.write_text(
                '<manifest><hal><name>vendor.foo</name>'
                '<fqname>@1.0::IFoo/default</fqname></hal>'
                '<hal><name>vendor.foo</name>'
                '<fqname>@1.0::IFoo/default</fqname></hal></manifest>'
            )
            errors, _ = MODULE.audit(path)
            self.assertTrue(any("duplicate HAL instance" in item for item in errors))

    def test_hal_without_name_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "manifest.xml"
            path.write_text('<manifest><hal><fqname>@1.0::IFoo/default</fqname></hal></manifest>')
            errors, count = MODULE.audit(path)
            self.assertTrue(any("has no <name>" in item for item in errors))
            self.assertEqual(count, 1)

    def test_empty_fqname_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "manifest.xml"
            path.write_text('<manifest><hal><name>vendor.foo</name><fqname> </fqname></hal></manifest>')
            errors, _ = MODULE.audit(path)
            self.assertTrue(any("empty <fqname>" in item for item in errors))

    def test_empty_fqname_is_reported_for_grouped_legacy_hal(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "manifest.xml"
            path.write_text('<manifest><hal><name>vendor.foo</name><name>vendor.bar</name><fqname> </fqname></hal></manifest>')
            errors, _ = MODULE.audit(path)
            self.assertTrue(any("empty <fqname>" in item for item in errors))

    def test_grouped_legacy_hal_names_are_not_misclassified(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "manifest.xml"
            path.write_text(
                '<manifest><hal><name>android.hardware.sensors</name>'
                '<name>android.frameworks.sensorservice</name>'
                '<fqname>@1.0::ISensors/default</fqname>'
                '<fqname>@1.0::ISensorManager/default</fqname>'
                '</hal></manifest>'
            )
            errors, count = MODULE.audit(path)
            self.assertEqual(errors, [])
            self.assertEqual(count, 1)

    def test_malformed_xml_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "broken.xml"
            path.write_text("<manifest><hal></manifest>")
            errors, count = MODULE.audit(path)
            self.assertTrue(any("XML parse failed" in item for item in errors))
            self.assertEqual(count, 0)

    def test_wrong_root_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "not-vintf.xml"
            path.write_text("<not-vintf />")
            errors, _ = MODULE.audit(path)
            self.assertTrue(any("unexpected root" in item for item in errors))


if __name__ == "__main__":
    unittest.main()
