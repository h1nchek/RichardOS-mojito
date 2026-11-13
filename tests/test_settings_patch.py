import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
PATCH = ROOT / "patches/lineage/Settings/0001-settings-add-richardos-dashboard.patch"


class RichardOSSettingsPatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.patch = PATCH.read_text()

    def test_apply_helper_accepts_repo_managed_git_metadata_file(self):
        helper = (ROOT / "scripts/apply-settings-patch.sh").read_text()
        self.assertIn('[[ ! -e "$SETTINGS_DIR/.git" ]]', helper)
        self.assertNotIn('[[ ! -d "$SETTINGS_DIR/.git" ]]', helper)

    def test_root_diagnostics_fragment_is_search_indexed(self):
        self.assertIn(
            "new BaseSearchIndexProvider(R.xml.richardos_root)",
            self.patch,
        )
        root_fragment = self.patch.split(
            "diff --git a/src/com/android/settings/richardos/RichardOSRootFragment.java",
            1,
        )[1]
        self.assertIn(
            "import com.android.settings.search.BaseSearchIndexProvider;",
            root_fragment,
        )

    def test_battery_values_match_lineage_sdk_contract(self):
        statusbar = self.patch.split(
            "diff --git a/res/values/richardos_arrays.xml",
            1,
        )[1].split("\ndiff --git ", 1)[0]
        self.assertIn(
            "<item>0</item><item>1</item><item>2</item><item>3</item>",
            statusbar,
        )
        self.assertIn(
            "<item>0</item><item>1</item><item>2</item>",
            statusbar,
        )

    def test_status_bar_fragment_uses_lineage_sdk_settings(self):
        self.assertIn(
            "LineageSettings.System.STATUS_BAR_BATTERY_STYLE",
            self.patch,
        )
        self.assertIn(
            "LineageSettings.System.STATUS_BAR_SHOW_BATTERY_PERCENT",
            self.patch,
        )
        self.assertIn(
            "import lineageos.providers.LineageSettings;",
            self.patch,
        )

    def test_lock_screen_entry_targets_existing_settings_fragment(self):
        self.assertIn(
            "com.android.settings.notification.LockScreenNotificationsPreferencePageFragment",
            self.patch,
        )

    def test_palette_uses_current_android_dynamic_color_contract(self):
        self.assertIn('android.theme.customization.theme_style', self.patch)
        self.assertIn('overlays.put(KEY_THEME_STYLE, "TONAL_SPOT")', self.patch)
        self.assertNotIn('overlays.put(KEY_ACCENT_COLOR, color)', self.patch)
        self.assertIn('overlays.remove(KEY_THEME_STYLE)', self.patch)

    def test_palette_selection_is_restored_from_secure_theme_state(self):
        self.assertIn('palette.setValue(getCurrentPalette())', self.patch)
        self.assertIn('Settings.Secure.THEME_CUSTOMIZATION_OVERLAY_PACKAGES', self.patch)
        self.assertIn('case "F5BE35": return "gold";', self.patch)
        self.assertIn('default: return "system";', self.patch)

    def test_unified_diff_hunk_line_counts_are_consistent(self):
        lines = self.patch.splitlines()
        hunk_re = re.compile(
            r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@"
        )
        checked = 0
        for index, line in enumerate(lines):
            match = hunk_re.match(line)
            if not match:
                continue
            old_expected = int(match.group(2) or "1")
            new_expected = int(match.group(4) or "1")
            old_actual = 0
            new_actual = 0
            for entry in lines[index + 1:]:
                if entry.startswith(("diff --git ", "@@ ")) or entry == "-- ":
                    break
                if entry.startswith("\\ No newline"):
                    continue
                if entry.startswith(" "):
                    old_actual += 1
                    new_actual += 1
                elif entry.startswith("+") and not entry.startswith("+++"):
                    new_actual += 1
                elif entry.startswith("-") and not entry.startswith("---"):
                    old_actual += 1
                if old_actual == old_expected and new_actual == new_expected:
                    break
            self.assertEqual(old_expected, old_actual, line)
            self.assertEqual(new_expected, new_actual, line)
            checked += 1
        self.assertGreater(checked, 0)


    def test_palette_choices_follow_richardos_graphite_and_gold_identity(self):
        self.assertIn("return 0xFFF5BE35;", self.patch)
        self.assertIn('case "graphite":', self.patch)
        self.assertIn("return 0xFF343840;", self.patch)
        self.assertIn('<item>RichardOS Gold</item>', self.patch)
        self.assertNotIn('case "ocean":', self.patch)
        self.assertNotIn('case "orchid":', self.patch)


if __name__ == "__main__":
    unittest.main()
