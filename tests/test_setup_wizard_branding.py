import pathlib
import unittest
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
SETUP = ROOT / "vendor/richardos/overlay/packages/apps/SetupWizard/res/values"


class RichardOSSetupWizardBrandingTest(unittest.TestCase):
    def test_setup_wizard_welcome_uses_richardos_name(self):
        root = ET.parse(SETUP / "strings.xml").getroot()
        values = {item.attrib["name"]: "".join(item.itertext()) for item in root}
        self.assertEqual(values["app_name"], "RichardOS Setup")
        self.assertEqual(values["os_name"], "RichardOS")
        self.assertEqual(
            values["setup_welcome_message"],
            "Welcome to %1$s",
        )
        self.assertEqual(values["setup_services"], "RichardOS features")
        self.assertIn("Diagnostic data", values["services_pp_explanation"])
        self.assertIn("RichardOS", values["services_help_improve_cm"])
        self.assertIn("diagnostic and usage data", values["services_metrics_label"])
        self.assertIn("%2$s", values["services_metrics_label"])
        self.assertIn("services_privacy_policy_uri", values)
        self.assertEqual(values["setup_navigation"], "Navigation")
        self.assertEqual(values["navigation_summary"], "Choose how you want to move around RichardOS")
        self.assertEqual(values["gesture_navigation"], "Gesture navigation")
        self.assertEqual(values["navbar_navigation"], "3-button navigation")
        self.assertEqual(values["setup_theme"], "Appearance")
        self.assertEqual(values["theme_summary"], "Choose the look of your device")

    def test_setup_wizard_overrides_verified_lineage24_colors(self):
        root = ET.parse(SETUP / "colors.xml").getroot()
        colors = {item.attrib["name"]: item.text.strip() for item in root.findall("color")}
        expected = {
            "lineage_accent": "#F5BE35",
            "button_bar_text_enabled": "#17191E",
            "button_bar_text_disabled": "#5217191E",
            "setup_compat_footer_primary_button_bg_color": "#F5BE35",
            "setup_compat_footer_primary_button_text_color": "#17191E",
            "materialColorPrimary": "#F5BE35",
            "materialColorOnPrimary": "#17191E",
            "finish_swipe_arrow": "#F5BE35",
        }
        for name, value in expected.items():
            self.assertEqual(colors[name], value)

    def test_welcome_layout_uses_existing_richardos_lion(self):
        layout = (SETUP.parent / "layout/welcome_activity.xml").read_text()
        self.assertIn('android:src="@drawable/richardos_lion"', layout)
        self.assertIn('android:id="@+id/brand_logo"', layout)
        self.assertIn("richardos_logo_description", layout)

    def test_finish_layout_uses_richardos_lion_and_keeps_finish_controls(self):
        layout = (SETUP.parent / "layout/finish_activity.xml").read_text()
        self.assertIn('android:id="@+id/brand_logo"', layout)
        self.assertIn('android:src="@drawable/richardos_lion"', layout)
        self.assertIn('android:id="@+id/background"', layout)
        self.assertIn('android:id="@+id/swipe_hint"', layout)
        self.assertIn('@string/swipe_up_to_go_home', layout)

    def test_installer_renders_existing_lion_asset(self):
        script = (ROOT / "scripts/install-system-branding.sh").read_text()
        self.assertIn('rsvg-convert --width 768 --height 768', script)
        self.assertIn('richardos_lion.png', script)
        self.assertIn('"$LOGO"', script)

    def test_installer_copies_and_registers_richardos_overlay(self):
        script = (ROOT / "scripts/install-system-branding.sh").read_text()
        self.assertIn(
            'cp -a "$ROOT/vendor/richardos/overlay/." "$ANDROID_TOP/vendor/richardos/overlay/"',
            script,
        )
        self.assertIn("PRODUCT_PACKAGE_OVERLAYS += vendor/richardos/overlay", script)


if __name__ == "__main__":
    unittest.main()
