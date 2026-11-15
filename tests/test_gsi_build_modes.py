from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class GsiBuildModeTests(unittest.TestCase):
    def test_baseline_is_the_default_and_does_not_apply_patches(self):
        script = (ROOT / "scripts/build-gsi.sh").read_text()
        self.assertIn('MODE="${RICHARDOS_GSI_MODE:-baseline}"', script)
        self.assertIn('if [[ "$MODE" == "richardos" ]]; then', script)
        self.assertIn('Baseline mode: no RichardOS patches will be applied.', script)
        self.assertIn('lunch gsi_arm64-userdebug', script)

    def test_integrated_mode_applies_only_reviewed_patch_set(self):
        script = (ROOT / "scripts/build-gsi.sh").read_text()
        for path in (
            "platform_system_netd/0001-netd-legacy-kernel-oneshot-nonfatal.patch",
            "platform_bionic/0001-epoll-pwait2-fallback-legacy-kernels.patch",
            "platform_frameworks_av/0001-camera-parameters-null-guard.patch",
            "Settings/0001-settings-add-richardos-dashboard.patch",
        ):
            self.assertIn(path, script)

    def test_build_checks_resolved_product_variant_and_device(self):
        script = (ROOT / "scripts/build-gsi.sh").read_text()
        self.assertIn('get_build_var TARGET_PRODUCT', script)
        self.assertIn('get_build_var TARGET_DEVICE', script)
        self.assertIn('get_build_var TARGET_BUILD_VARIANT', script)
        self.assertIn('"$actual_product" == "gsi_arm64"', script)
        self.assertIn('"$actual_device" == "generic_arm64"', script)
        self.assertIn('"$actual_variant" == "userdebug"', script)

    def test_workflow_defaults_to_baseline_and_exposes_integration_choice(self):
        workflow = (ROOT / ".github/workflows/build-gsi.yml").read_text()
        self.assertIn("default: baseline", workflow)
        self.assertIn("- baseline", workflow)
        self.assertIn("- richardos", workflow)
        self.assertIn("RICHARDOS_GSI_MODE: ${{ inputs.mode }}", workflow)

    def test_build_records_pinned_manifest_and_image_metadata(self):
        script = (ROOT / "scripts/build-gsi.sh").read_text()
        self.assertIn('repo manifest -r -o "$OUT_DIR/manifest.lock.xml"', script)
        self.assertIn('MANIFEST_SHA256=%s', script)
        self.assertIn('IMAGE_SHA256=%s', script)
        self.assertIn('richardos-build-info.txt', script)


if __name__ == "__main__":
    unittest.main()
