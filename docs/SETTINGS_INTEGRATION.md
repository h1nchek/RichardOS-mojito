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
mark, and opens a native dashboard with the four planned sections. Status Bar,
Root & System now opens a read-only diagnostics page; Status Bar and Lock Screen remain placeholders. Monet has a
native palette selector that writes curated seed colors to the existing
SystemUI theme customization setting, while System default removes RichardOS
overrides to restore wallpaper-derived colors.

Apply it to a clean Settings checkout on `lineage-24.0` with:

```bash
bash scripts/apply-settings-patch.sh /path/to/lineage/packages/apps/Settings
```

The helper verifies the repository remote and branch, checks for local changes,
and runs `git apply --check` before applying. The patch has not yet been
applied to a full synced Android tree or compiled. Do not treat it as a tested
ROM feature until Settings builds successfully.


### Fragment allowlist

The dashboard fragment is registered in
`src/com/android/settings/core/gateway/SettingsGateway.java` via
`ENTRY_FRAGMENTS`. This is required because `SettingsActivity` validates
fragment names before displaying them. The integration patch adds both the
import and the allowlist entry.


### Monet palette application (initial implementation)

The dashboard includes a native `ListPreference` with System default, Ocean,
Sage, Orchid, Ember, Graphite, and Rose presets. On selection, the fragment
updates `Settings.Secure.THEME_CUSTOMIZATION_OVERLAY_PACKAGES`, preserving
unrelated JSON entries. Presets set both `android.theme.customization.system_palette`
and `android.theme.customization.accent_color`, with color source `preset`;
System default removes these overrides so SystemUI can use wallpaper-derived
colors again. The platform's existing SystemUI theme controller consumes this
setting and generates the dynamic tonal resources.

This is source-level implementation only. It has not been applied to a full
synced checkout, compiled, or verified on a phone. The feature depends on the
target branch's existing SystemUI theme controller being active.


### Root & System diagnostics (initial implementation)

The Root & System page is a native Settings fragment and reports Android release/API
level, build display and type, build fingerprint, manufacturer/model/device codename,
kernel version, active A/B boot slot when exposed, Android security patch level,
SELinux mode, data-encryption state, dm-verity mode, Verified Boot state, and
bootloader lock state. It reads platform build/security properties only and does
not change device state.

Root status is intentionally shown as **Not assessed**. A generic scan for a
`su` binary or root-manager package is not reliable enough to claim that a device
is or is not rooted. No root-hiding, integrity spoofing, bootloader bypass, or
automatic root-management actions are implemented.

Boot slot, dm-verity, Verified Boot, and bootloader fields depend on
bootloader-provided properties; if the device does not expose them, the page
displays **Unknown**. Build fingerprint and build type are informational and
should not be interpreted as a security verdict. The
implementation uses platform APIs/properties available to the privileged
Settings build and has not yet been compiled or tested on hardware.


### Status Bar & Quick Settings (initial implementation)

The dashboard opens a native RichardOS Settings fragment with two controls backed by
LineageOS's existing `LineageSettings.System` provider:

- Battery icon style: default, circle, text, or dotted circle.
- Battery percentage: hidden, inside the icon, or next to the icon.

The option values and setting keys were checked against the LineageOS 24.0
Lineage SDK and SystemUI battery repository. Quick Settings tile arrangement is
not duplicated in RichardOS: users continue to edit tiles from the native shade
editor. The fragment is source-level only and has not been compiled or tested
on-device.
