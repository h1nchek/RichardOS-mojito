# RichardOS integration with LineageOS Settings

## Target

- Upstream repository: `LineageOS/android_packages_apps_Settings`
- Target branch: `lineage-24.0`
- RichardOS Hub must be a native section inside the existing Settings APK.
- Do not create a separate RichardOSHub application or APK.

## Verified upstream structure

The following files were inspected on the `lineage-24.0` branch:

- `src/com/android/settings/system/SystemDashboardFragment.java`
  - Uses `DashboardFragment`, `getPreferenceScreenResId()`,
    `SettingsEnums`, and `BaseSearchIndexProvider`.
- `res/xml/top_level_settings.xml`
  - Home page entries use `com.android.settings.widget.HomepagePreference`
    and point to a fragment with `android:fragment`.
- `AndroidManifest.xml`
  - Declares the existing Settings package as `com.android.settings`.

This confirms the integration direction: RichardOS adds a DashboardFragment
and preference resources to the existing Settings source tree, then registers the
entry in the top-level Settings preference screen. It does not add a new
standalone app or package.

## Planned implementation

Proposed source location inside the upstream Settings repository:

```text
src/com/android/settings/richardos/
  RichardOSDashboardFragment.java
  themes/
  statusbar/
  root/
  lockscreen/
res/xml/
  richardos_dashboard.xml
res/values/
  richardos_strings.xml
```

The exact package, metrics category, preference keys, resource names, and
navigation behavior must follow the target branch's existing conventions.
The dashboard entry will be added to `top_level_settings.xml`.

## First functional milestone

The first milestone is deliberately small:

1. Add a RichardOS entry to the main Settings screen.
2. Open an in-Settings RichardOS dashboard.
3. Show four sections: Monet & Themes, Status Bar & Quick Settings,
   Root & System, and Lock Screen.
4. Implement Monet preferences first, using supported Android color APIs.
5. Keep unfinished controls hidden or clearly unavailable; do not expose
   nonfunctional switches.

Root & System is a read-only diagnostics area. It must not attempt to hide
root, spoof device integrity, bypass verified boot, or change bootloader state.

## Patch status

An experimental patch is now available at
`patches/lineage/Settings/0001-settings-add-richardos-dashboard.patch`.
It adds a RichardOS entry to the Settings homepage, uses the gold lion vector
mark, and opens a native dashboard with the four planned sections. The section
rows are deliberately non-clickable placeholders; no Monet controls or saved
palette state have been implemented yet.

Apply it to a clean Settings checkout on `lineage-24.0` with:

```bash
bash scripts/apply-settings-patch.sh /path/to/lineage/packages/apps/Settings
```

The helper verifies the repository remote and branch, checks for local changes,
and runs `git apply --check` before applying. The patch has not yet been
applied to a full synced Android tree or compiled. Do not treat it as a tested
ROM feature until Settings builds successfully.
