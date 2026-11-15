"""Static safety and integration checks for the Font Studio prototype."""

from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "vendor/richardos/fontstudio"
JAVA = APP / "src/com/richardos/fontstudio/FontStudioActivity.java"


class FontStudioPrototypeTests(unittest.TestCase):
    def test_android_module_and_launcher_activity_exist(self):
        self.assertTrue((APP / "Android.bp").is_file())
        manifest = ET.parse(APP / "AndroidManifest.xml").getroot()
        activity = manifest.find("./application/activity")
        self.assertIsNotNone(activity)
        self.assertEqual("true", activity.attrib[
            "{http://schemas.android.com/apk/res/android}exported"
        ])
        self.assertTrue(any(
            item.attrib.get("{http://schemas.android.com/apk/res/android}name")
            == "android.intent.action.MAIN"
            for item in activity.findall("./intent-filter/action")
        ))

    def test_import_is_private_bounded_and_parser_validated(self):
        source = JAVA.read_text()
        self.assertIn("getFilesDir()", source)
        self.assertIn("MAX_FONT_BYTES = 20L * 1024L * 1024L", source)
        self.assertIn("Typeface.createFromFile(temporary)", source)
        self.assertIn("hasSupportedSfntHeader(temporary)", source)
        self.assertIn("a == 'O' && b == 'T' && c == 'T' && d == 'O'", source)
        self.assertIn("total < 12", source)
        self.assertIn("Intent.ACTION_OPEN_DOCUMENT", source)
        self.assertNotIn("MANAGE_EXTERNAL_STORAGE", source)
        self.assertNotIn("/system/fonts", source)
        self.assertNotIn("Runtime.getRuntime().exec", source)

    def test_import_transaction_recovers_previous_font(self):
        source = JAVA.read_text()
        self.assertIn("recoverInterruptedImport()", source)
        self.assertIn("if (!customFont.exists() && backupFont.isFile())", source)
        self.assertIn("if (hadPrevious && !backupFont.renameTo(customFont))", source)
        self.assertIn("recovery copy retained at", source)
        self.assertIn("A previous font recovery file needs attention", source)

    def test_product_includes_the_font_studio_module(self):
        product_config = (ROOT / "vendor/richardos/config/branding.mk").read_text()
        module = (APP / "Android.bp").read_text()
        self.assertIn("RichardOSFontStudio", product_config)
        self.assertIn('name: "RichardOSFontStudio"', module)
        self.assertIn("system_ext_specific: true", module)

    def test_font_studio_is_mojito_only_not_generic_gsi(self):
        product_config = (ROOT / "vendor/richardos/config/branding.mk").read_text()
        self.assertIn("Included at the end of the mojito product makefile", product_config)
        gsi_root = ROOT / "gsi"
        for path in gsi_root.rglob("*"):
            if path.is_file() and path.suffix in {".mk", ".bp", ".json", ".py", ".sh"}:
                self.assertNotIn("RichardOSFontStudio", path.read_text(errors="replace"))

    def test_custom_font_is_previewed_and_selection_persisted(self):
        source = JAVA.read_text()
        self.assertIn("preview.setTypeface(candidate)", source)
        self.assertIn('saveSelection("custom")', source)
        self.assertIn('prefs.getString(KEY_SELECTION, "preset:sans-serif")', source)
        self.assertIn("Typeface.createFromFile(customFont)", source)

    def test_settings_dashboard_opens_font_studio_app(self):
        patch = (
            ROOT / "patches/lineage/Settings/"
            "0001-settings-add-richardos-dashboard.patch"
        ).read_text()
        self.assertIn('android:key="richardos_font_studio"', patch)
        self.assertIn('intent.setClassName("com.richardos.fontstudio"', patch)
        self.assertIn("richardos_font_studio_unavailable", patch)

    def test_font_manager_plan_matches_lineage24_api_and_security_gates(self):
        design = (ROOT / "docs/features/font-studio.md").read_text()
        self.assertIn("FontUpdateRequest", design)
        self.assertIn("UPDATE_FONTS", design)
        self.assertIn("fs-verity", design)
        self.assertIn("config_fontManagerServiceCerts", design)
        self.assertIn("RESULT_ERROR_FONT_UPDATER_DISABLED", design)
        self.assertNotIn("FontFamilyUpdateRequest", design)
        self.assertNotIn("FontFileUpdateRequest", design)

    def test_prototype_does_not_claim_system_wide_apply(self):
        source = JAVA.read_text()
        readme = (APP / "README.md").read_text()
        self.assertIn("System-wide font replacement is not implemented", source)
        self.assertIn("does not change Settings, SystemUI", readme)


if __name__ == "__main__":
    unittest.main()
