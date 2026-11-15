"""Static safety and integration checks for the Font Studio prototype."""

from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "vendor/richardos/fontstudio"


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
        source = (APP / "src/com/richardos/fontstudio/FontStudioActivity.java").read_text()
        self.assertIn("getFilesDir()", source)
        self.assertIn("MAX_FONT_BYTES = 20L * 1024L * 1024L", source)
        self.assertIn("Typeface.createFromFile(temporary)", source)
        self.assertIn("Intent.ACTION_OPEN_DOCUMENT", source)
        self.assertNotIn("MANAGE_EXTERNAL_STORAGE", source)
        self.assertNotIn("/system/fonts", source)
        self.assertNotIn("Runtime.getRuntime().exec", source)

    def test_product_includes_the_font_studio_module(self):
        product_config = (ROOT / "vendor/richardos/config/branding.mk").read_text()
        module = (APP / "Android.bp").read_text()
        self.assertIn("RichardOSFontStudio", product_config)
        self.assertIn('name: "RichardOSFontStudio"', module)
        self.assertIn("system_ext_specific: true", module)

    def test_prototype_does_not_claim_system_wide_apply(self):
        source = (APP / "src/com/richardos/fontstudio/FontStudioActivity.java").read_text()
        readme = (APP / "README.md").read_text()
        self.assertIn("System-wide font replacement is not implemented", source)
        self.assertIn("does not change Settings, SystemUI", readme)


if __name__ == "__main__":
    unittest.main()
