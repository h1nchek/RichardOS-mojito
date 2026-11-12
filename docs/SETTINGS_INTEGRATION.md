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

This confirms the integration direction: RichardOS should add a DashboardFragment
and preference resources to the existing Settings source tree, then register the
entry in the top-level Settings preference screen. It should not add a new
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

## Validation status

The upstream branch and representative integration files have been inspected.
No patch has yet been applied to a complete synced Settings checkout, and no
Android compilation has been run. The repository currently contains the design
and integration plan only; it does not claim that the Hub is implemented.
