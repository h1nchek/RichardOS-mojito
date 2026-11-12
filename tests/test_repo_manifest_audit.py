import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from audit_repo_manifests import validate_manifest


class RepoManifestAuditTests(unittest.TestCase):
    def check_xml(self, xml):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        path = Path(temp.name) / "manifest.xml"
        path.write_text(xml, encoding="utf-8")
        return validate_manifest(path)

    def test_accepts_valid_project(self):
        self.assertEqual([], self.check_xml(
            '<manifest><remote name="x" fetch="https://example.invalid"/>'
            '<project name="device" path="device/x" remote="x" revision="17.0"/>'
            '</manifest>'))

    def test_rejects_duplicate_paths(self):
        errors = self.check_xml(
            '<manifest><remote name="x" fetch="https://example.invalid"/>'
            '<project name="one" path="device/x" remote="x" revision="17.0"/>'
            '<project name="two" path="device/x" remote="x" revision="17.0"/>'
            '</manifest>')
        self.assertTrue(any("duplicate project path" in item for item in errors))

    def test_rejects_undeclared_remote(self):
        errors = self.check_xml(
            '<manifest><project name="one" remote="missing" revision="17.0"/>'
            '</manifest>')
        self.assertTrue(any("undeclared remote" in item for item in errors))

    def test_rejects_missing_revision(self):
        errors = self.check_xml(
            '<manifest><remote name="x" fetch="https://example.invalid"/>'
            '<project name="one" remote="x"/></manifest>')
        self.assertTrue(any("missing revision" in item for item in errors))

    def test_accepts_extend_project_with_name(self):
        self.assertEqual([], self.check_xml(
            '<manifest><extend-project name="LineageOS/android_frameworks_base" '
            'path="frameworks/base" revision="abc123"/></manifest>'))

    def test_rejects_extend_project_without_name(self):
        errors = self.check_xml(
            '<manifest><extend-project path="frameworks/base" '
            'revision="abc123"/></manifest>')
        self.assertTrue(any("missing required name" in item for item in errors))

    def test_rejects_invalid_xml(self):
        self.assertTrue(self.check_xml("<manifest>"))
