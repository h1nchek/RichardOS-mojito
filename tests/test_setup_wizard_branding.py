import pathlib
import unittest
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
SETUP = ROOT / "vendor/richardos/overlay/packages/apps/SetupWizard/res/values"

class RichardOSSetupWizardBrandingTest(unittest.TestCase):
    def test_setup_wizard_strings_are_branded(self):
        root = ET.parse(SETUP / "strings.xml").getroot()
        values = {item.attrib["name"]: "".join(item.itertext()) for item in root}
        self.assertEqual(values["app_name"], "RichardOS Setup")
        self.assertEqual(values["os_name"], "RichardOS")
        self.assertIn("RichardOS", values["setup_welcome_message"])
        self.assertEqual(values["setup_services"], "RichardOS features")

    def test_setup_wizard_uses_richardos_gold_accent(self):
        root = ET.parse(SETUP / "colors.xml").getroot()
        colors = {item.attrib["name"]: item.text for item in root.findall("color")}
        self.assertEqual(colors["lineage_accent"], "#F5BE35")
        self.assertIn("button_bar_text_enabled", colors)
        self.assertIn("divider", colors)

    def test_system_branding_installer_copies_setup_wizard_overlay(self):
        script = (ROOT / "scripts/install-system-branding.sh").read_text()
        self.assertIn('cp -a "$ROOT/vendor/richardos/overlay/." "$ANDROID_TOP/vendor/richardos/overlay/"', script)

if __name__ == "__main__":
    unittest.main()
