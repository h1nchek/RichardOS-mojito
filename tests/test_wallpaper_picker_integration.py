import pathlib
import re
import unittest
import xml.etree.ElementTree as ET


ROOT = pathlib.Path(__file__).resolve().parents[1]
WALLPAPER_DIR = ROOT / "vendor/richardos/wallpapers"
ARTWORK_DIR = ROOT / "vendor/richardos/branding/wallpapers"


class WallpaperPickerIntegrationTest(unittest.TestCase):
    def test_partner_array_matches_all_artwork_assets(self):
        root = ET.parse(WALLPAPER_DIR / "res/values/arrays.xml").getroot()
        array = root.find("./string-array[@name='partner_wallpapers']")
        self.assertIsNotNone(array)
        names = [item.text for item in array.findall("item")]
        self.assertEqual(
            names,
            ["richardos_nocturne", "richardos_eclipse", "richardos_aurum"],
        )
        installer = (ROOT / "scripts/install-wallpaper-picker.sh").read_text()
        for name in names:
            self.assertIn(f"render {name} ", installer)
            self.assertTrue((ARTWORK_DIR / (name.replace("_", "-") + ".svg")).is_file())

    def test_partner_receiver_is_discoverable(self):
        manifest = ET.parse(WALLPAPER_DIR / "AndroidManifest.xml").getroot()
        receiver = manifest.find("./application/receiver")
        self.assertIsNotNone(receiver)
        self.assertEqual(receiver.attrib.get("{http://schemas.android.com/apk/res/android}exported"), "true")
        actions = [
            node.attrib.get("{http://schemas.android.com/apk/res/android}name")
            for node in receiver.findall("./intent-filter/action")
        ]
        self.assertIn("com.android.launcher3.action.PARTNER_CUSTOMIZATION", actions)

    def test_product_installer_registers_the_module(self):
        installer = (ROOT / "scripts/install-wallpaper-picker.sh").read_text()
        self.assertIn("PRODUCT_PACKAGES += RichardOSWallpapers", installer)
        bp = (WALLPAPER_DIR / "Android.bp").read_text()
        self.assertIn('name: "RichardOSWallpapers"', bp)
        self.assertIn("system_ext_specific: true", bp)


if __name__ == "__main__":
    unittest.main()
