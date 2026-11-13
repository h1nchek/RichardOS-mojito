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

    def test_both_stages_run_the_read_only_host_preflight(self):
        baseline = (ROOT / "scripts/build-baseline.sh").read_text()
        custom = (ROOT / "scripts/build.sh").read_text()
        host = (ROOT / "scripts/check-build-host.sh").read_text()
        self.assertIn("check-build-host.sh\" post-sync", baseline)
        self.assertIn("check-build-host.sh\" pre-sync", custom)
        self.assertIn("MIN_FREE_GB=350", host)
        self.assertIn("MIN_FREE_GB=80", host)
        self.assertIn("CPUS >= 8", host)
        self.assertIn("MEMORY_GB >= 32", host)

    def test_dependency_preflight_is_read_only_and_wired_into_both_build_stages(self):
        deps = (ROOT / "scripts/check-build-deps.sh").read_text()
        baseline = (ROOT / "scripts/build-baseline.sh").read_text()
        custom = (ROOT / "scripts/build.sh").read_text()
        self.assertIn("dpkg-query", deps)
        self.assertIn("lib32readline-dev", deps)
        self.assertIn("python3-protobuf", deps)
        self.assertIn("librsvg2-bin", deps)
        self.assertIn("check-build-deps.sh", baseline)
        self.assertIn("check-build-deps.sh", custom)
        self.assertNotIn("apt-get install", deps.split("Suggested install command")[0])

    def test_first_build_documentation_keeps_two_stages_separate(self):
        doc = (ROOT / "docs/FIRST_BUILD.md").read_text()
        self.assertIn("build-baseline.sh", doc)
        self.assertIn("scripts/build.sh", doc)
        self.assertIn("does **not** apply RichardOS branding", doc)


if __name__ == "__main__":
    unittest.main()
