import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class RichardOSBuildPipelineTests(unittest.TestCase):
    def test_baseline_stage_does_not_apply_richardos_customizations(self):
        script = (ROOT / "scripts/build-baseline.sh").read_text()
        self.assertIn("audit_manifest_dependencies.py", script)
        self.assertIn("device/qcom/sepolicy_vndr/SEPolicy.mk", script)
        self.assertNotIn("install-system-branding.sh", script)
        self.assertNotIn("apply-settings-patch.sh", script)

    def test_custom_rom_stage_applies_settings_hub_before_build(self):
        script = (ROOT / "scripts/build.sh").read_text()
        self.assertIn("audit_manifest_dependencies.py", script)
        patch = script.index("apply-settings-patch.sh")
        build = script.index('m bacon -j"$JOBS"')
        self.assertLess(patch, build)
        self.assertIn('git -C "$ANDROID_DIR/packages/apps/Settings" diff --check', script)

    def test_first_build_documentation_keeps_two_stages_separate(self):
        doc = (ROOT / "docs/FIRST_BUILD.md").read_text()
        self.assertIn("build-baseline.sh", doc)
        self.assertIn("scripts/build.sh", doc)
        self.assertIn("does **not** apply RichardOS branding", doc)


if __name__ == "__main__":
    unittest.main()
