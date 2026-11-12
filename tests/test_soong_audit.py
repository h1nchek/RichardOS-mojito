import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "audit-soong-deps.py"
SPEC = importlib.util.spec_from_file_location("soong_audit", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class SoongAuditTests(unittest.TestCase):
    def test_indexes_module_names_and_dependency_arrays(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "Android.bp"
            path.write_text(
                'cc_prebuilt_library_shared {\n'
                '  name: "libalpha",\n'
                '  shared_libs: ["libbeta", "libc"],\n'
                '  static_libs: ["libsupport"],\n'
                '  defaults: ["common_defaults"],\n'
                '}\n'
                'cc_library { name: "libbeta" }\n'
            )
            modules = MODULE.parse_modules(path)
            self.assertEqual([item.name for item in modules], ["libalpha", "libbeta"])
            self.assertEqual(
                modules[0].dependencies["shared_libs"], ["libbeta", "libc"]
            )
            self.assertEqual(
                modules[0].dependencies["static_libs"], ["libsupport"]
            )
            self.assertEqual(
                modules[0].dependencies["defaults"], ["common_defaults"]
            )

    def test_ignores_nested_properties_and_comments(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "Android.bp"
            path.write_text(
                '// comment with fake_module { name: "bad" }\n'
                'cc_library {\n'
                ' name: "real",\n'
                ' target: { android: { shared_libs: ["nested"] } },\n'
                ' shared_libs: ["actual"],\n'
                '}\n'
            )
            modules = MODULE.parse_modules(path)
            self.assertEqual(len(modules), 1)
            self.assertEqual(modules[0].name, "real")
            self.assertEqual(modules[0].dependencies["shared_libs"], ["nested", "actual"])

    def test_unterminated_module_block_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "Android.bp"
            path.write_text('cc_library { name: "libalpha", shared_libs: ["libbeta"]')
            with self.assertRaisesRegex(ValueError, "unterminated block"):
                MODULE.parse_modules(path)

    def test_cli_returns_two_for_malformed_android_bp(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "Android.bp"
            path.write_text('cc_library { name: "libalpha"')
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(path)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("ERROR malformed Android.bp", result.stderr)

    def test_cli_strict_returns_one_for_unindexed_dependency(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "Android.bp"
            path.write_text(
                'cc_library { name: "libalpha", shared_libs: ["libexternal"] }'
            )
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--strict", str(path)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("UNINDEXED libalpha", result.stdout)

    def test_strict_mode_flags_unindexed_dependency(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "Android.bp"
            path.write_text(
                'cc_library { name: "libalpha", shared_libs: ["libexternal"] }'
            )
            modules = MODULE.parse_modules(path)
            self.assertEqual(len(modules), 1)
            self.assertEqual(
                modules[0].dependencies["shared_libs"], ["libexternal"]
            )


if __name__ == "__main__":
    unittest.main()
