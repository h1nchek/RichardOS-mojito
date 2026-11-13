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
        self.assertIn('check-build-deps.sh" baseline', baseline)
        self.assertIn('check-build-deps.sh"\n', custom)
        self.assertIn('MODE="${1:-full}"', deps)
        self.assertIn('[[ "$MODE" == full ]]', deps)
        self.assertNotIn("apt-get install", deps.split("Suggested install command")[0])

    def test_first_build_documentation_keeps_two_stages_separate(self):
        doc = (ROOT / "docs/FIRST_BUILD.md").read_text()
        self.assertIn("build-baseline.sh", doc)
        self.assertIn("scripts/build.sh", doc)
        self.assertIn("does **not** apply RichardOS branding", doc)

    def test_gsi_checker_validates_upstream_product_definition(self):
        import subprocess
        import tempfile

        checker = ROOT / "scripts/check-gsi-config.py"
        with tempfile.TemporaryDirectory() as directory:
            product = pathlib.Path(directory) / "gsi_arm64.mk"
            product.write_text(
                "$(call inherit-product, $(SRC_TARGET_DIR)/product/core_64_bit.mk)\n"
                "$(call inherit-product, $(SRC_TARGET_DIR)/product/generic_system.mk)\n"
                "$(call inherit-product, device/generic/common/gsi_system_ext.mk)\n"
                "$(call inherit-product, device/generic/common/gsi_product.mk)\n"
                "$(call inherit-product, $(SRC_TARGET_DIR)/product/gsi_release.mk)\n"
                "PRODUCT_NAME := gsi_arm64\n"
                "PRODUCT_DEVICE := generic_arm64\n"
                "PRODUCT_SOONG_DEFINED_SYSTEM_IMAGE := android_gsi\n"
                "USE_SOONG_DEFINED_SYSTEM_IMAGE := true\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                ["python3", str(checker), str(product)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            product.write_text("PRODUCT_NAME := wrong_target\n", encoding="utf-8")
            result = subprocess.run(
                ["python3", str(checker), str(product)],
                capture_output=True, text=True, check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("PRODUCT_NAME", result.stderr)

    def test_gsi_source_set_rejects_mojito_specific_references(self):
        import shutil
        import subprocess
        import tempfile

        checker = ROOT / "scripts/check-gsi-config.py"
        with tempfile.TemporaryDirectory() as directory:
            temp_root = pathlib.Path(directory)
            shutil.copytree(ROOT / "gsi", temp_root / "gsi")
            clean = subprocess.run(
                ["python3", str(checker), "--repo-root", str(temp_root)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(clean.returncode, 0, clean.stderr)
            (temp_root / "gsi" / "accidental-device-reference.mk").write_text(
                "# device/xiaomi/mojito must never enter a generic GSI source set\\n",
                encoding="utf-8",
            )
            contaminated = subprocess.run(
                ["python3", str(checker), "--repo-root", str(temp_root)],
                capture_output=True, text=True, check=False,
            )
            self.assertNotEqual(contaminated.returncode, 0)
            self.assertIn("Xiaomi mojito-specific", contaminated.stderr)

    def test_experimental_gsi_metadata_is_explicitly_unbuilt(self):
        import json
        config = json.loads((ROOT / "gsi/targets.json").read_text())
        self.assertEqual(config["target"]["name"], "gsi_arm64")
        self.assertEqual(config["target"]["architecture"], "arm64")
        self.assertEqual(config["target"]["binder_bitness"], 64)
        self.assertEqual(config["target"]["lunch_alias"], "unverified")
        self.assertFalse(config["image_built"])
        self.assertFalse(config["device_tested"])
        self.assertTrue((ROOT / "gsi/GSI_TESTING.md").is_file())


if __name__ == "__main__":
    unittest.main()
