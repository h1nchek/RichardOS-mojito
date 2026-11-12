import pathlib
import unittest
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
CONTACTS = ROOT / "vendor/richardos/overlay/packages/apps/Contacts/res/values/colors.xml"

class RichardOSSystemAppBrandingTest(unittest.TestCase):
    def test_contacts_overlay_uses_gold_accents(self):
        root = ET.parse(CONTACTS).getroot()
        colors = {item.attrib["name"]: item.text for item in root.findall("color")}
        self.assertEqual(colors["primary_color"], "#B98A18")
        self.assertEqual(colors["primary_color_dark"], "#76530A")
        self.assertEqual(colors["fab_color"], "#F5BE35")
        self.assertIn("action_bar_background", colors)

    def test_contacts_overlay_is_inside_shared_product_overlay(self):
        self.assertEqual(
            CONTACTS.relative_to(ROOT / "vendor/richardos/overlay").as_posix(),
            "packages/apps/Contacts/res/values/colors.xml",
        )

if __name__ == "__main__":
    unittest.main()
