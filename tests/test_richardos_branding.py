import pathlib
import re
import unittest
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
OVERLAY = ROOT / "vendor/richardos/overlay/frameworks/base/core/res/res/values/colors.xml"

class RichardOSBrandingTest(unittest.TestCase):
    def test_material_you_gold_palette_has_light_and_dark_tones(self):
        root = ET.parse(OVERLAY).getroot()
        names = {item.attrib["name"] for item in root.findall("color")}
        for palette in ("system_accent1", "system_accent2", "system_accent3"):
            for tone in (10, 50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000):
                for mode in ("light", "dark"):
                    self.assertIn(f"{palette}_{tone}_{mode}", names)

    def test_product_identity_does_not_override_lunch_product_name(self):
        content = (ROOT / "vendor/richardos/config/branding.mk").read_text()
        self.assertNotRegex(content, r"(?m)^PRODUCT_NAME\\s*[:+]?=")
        self.assertIn("PRODUCT_BRAND := RichardOS", content)
        self.assertIn("PRODUCT_MODEL := Redmi Note 10", content)

    def test_build_installs_branding_before_compilation(self):
        build = (ROOT / "scripts/build.sh").read_text()
        self.assertIn('bash "$ROOT/scripts/install-system-branding.sh" "$ANDROID_DIR"', build)
        self.assertIn('m bacon -j"$JOBS"', build)

    def test_boot_animation_installer_generates_1080p_zip(self):
        script = (ROOT / "scripts/install-system-branding.sh").read_text()
        self.assertIn("1080 2400 30", script)
        self.assertIn("system/media/bootanimation.zip", script)
        self.assertIn("PRODUCT_NAME := lineage_mojito", script)

if __name__ == "__main__":
    unittest.main()
