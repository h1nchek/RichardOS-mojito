"""Static integrity checks for the native RichardOS Settings patch."""

from __future__ import annotations

import pathlib
import re
import unittest
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
PATCH = ROOT / "patches/lineage/Settings/0001-settings-add-richardos-dashboard.patch"


def added_files(patch: str) -> dict[str, str]:
    files: dict[str, list[str]] = {}
    current: str | None = None
    for line in patch.splitlines():
        if line.startswith("+++ b/"):
            current = line[6:]
            files[current] = []
        elif current is not None and line.startswith("+") and not line.startswith("+++"):
            files[current].append(line[1:])
        elif line.startswith("diff --git "):
            current = None
    return {path: "\n".join(lines) + "\n" for path, lines in files.items()}


class RichardOSSettingsResourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.patch = PATCH.read_text(encoding="utf-8")
        cls.files = added_files(cls.patch)
        cls.xml_files = {
            path: ET.fromstring(content)
            for path, content in cls.files.items()
            if path.endswith(".xml")
        }

    def test_all_added_settings_xml_is_well_formed(self):
        self.assertGreater(len(self.xml_files), 0)

    def test_richardos_resource_references_are_declared(self):
        declared: set[str] = set()
        for path, root in self.xml_files.items():
            if path.startswith("res/values/"):
                for item in root:
                    name = item.attrib.get("name")
                    if name:
                        declared.add(name)

        references: set[str] = set()
        for root in self.xml_files.values():
            for element in root.iter():
                for value in element.attrib.values():
                    references.update(
                        re.findall(r"@(?:string|array|xml|drawable)/((?:richardos_)[A-Za-z0-9_]+)", value)
                    )
        missing = sorted(references - declared)
        self.assertEqual([], missing, f"Missing RichardOS resources: {missing}")

    def test_palette_entries_and_values_have_matching_lengths(self):
        arrays = self.xml_files["res/values/richardos_arrays.xml"]
        found = {
            item.attrib["name"]: [entry.text or "" for entry in item.findall("item")]
            for item in arrays.findall("string-array")
        }
        self.assertEqual(
            len(found["richardos_palette_entries"]),
            len(found["richardos_palette_values"]),
        )
        self.assertEqual(
            len(found["richardos_battery_style_entries"]),
            len(found["richardos_battery_style_values"]),
        )
        self.assertEqual(
            len(found["richardos_battery_percent_entries"]),
            len(found["richardos_battery_percent_values"]),
        )
        for name, values in found.items():
            if name.endswith("_values"):
                self.assertEqual(len(values), len(set(values)), name)

    def test_richardos_fragments_are_registered_in_settings_gateway(self):
        gateway = self.files[
            "src/com/android/settings/core/gateway/SettingsGateway.java"
        ]
        for class_name in (
            "RichardOSDashboardFragment",
            "RichardOSStatusBarFragment",
            "RichardOSRootFragment",
        ):
            with self.subTest(fragment=class_name):
                source = (
                    "src/com/android/settings/richardos/" + class_name + ".java"
                )
                self.assertIn(source, self.files)
                self.assertIn(
                    "com.android.settings.richardos." + class_name,
                    gateway,
                )

    def test_dashboard_fragment_targets_are_present_or_upstream(self):
        dashboard = self.xml_files["res/xml/richardos_dashboard.xml"]
        fragments = [
            element.attrib["{http://schemas.android.com/apk/res/android}fragment"]
            for element in dashboard.iter()
            if "{http://schemas.android.com/apk/res/android}fragment" in element.attrib
        ]
        self.assertIn(
            "com.android.settings.richardos.RichardOSStatusBarFragment", fragments
        )
        self.assertIn(
            "com.android.settings.richardos.RichardOSRootFragment", fragments
        )
        self.assertIn(
            "com.android.settings.notification.LockScreenNotificationsPreferencePageFragment",
            fragments,
        )


if __name__ == "__main__":
    unittest.main()
