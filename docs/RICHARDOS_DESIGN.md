# RichardOS — product and interface direction

> Status: proposal only. None of the features below are implemented yet.

RichardOS is a LineageOS-based ROM for the Xiaomi Redmi Note 10 (`mojito`). Its goal is to keep the clean, restrained feel of Pixel software while adding a small set of useful controls that are genuinely part of the operating system.

## Product principles

1. **Quiet by default.** The interface should feel clean and predictable, not overloaded with toggles.
2. **Useful customization.** Every added option should solve a real use case and have a clear default.
3. **Native integration.** Prefer Android framework, SystemUI, Settings, and resource overlays over separate background apps or persistent services.
4. **Respect platform behavior.** Preserve Android permission, privacy, battery, and security expectations.
5. **Upstream-aware.** Keep changes modular and document the upstream component and reason for each patch.

## Visual direction

- Pixel-inspired Material You language, without copying Pixel branding or proprietary assets.
- Dynamic color where supported by the platform.
- Consistent spacing, typography, icon weight, corner radii, and animation timing.
- Avoid excessive blur, gradients, and permanent on-screen controls.
- Keep accessibility: readable contrast, scalable text, and clear labels.

## Feature proposals

### 1. RichardOS Settings
A dedicated section in Settings for ROM-specific options. It should contain only options that are not already available in standard Android Settings.

### 2. Quick Settings controls
A small, curated set of optional controls:
- Status-bar clock: show/hide seconds and choose left/center/right alignment only if the platform layout can support it cleanly.
- Status-bar indicators: independently show or hide selected non-essential indicators.
- Quick Settings layout: optional row/column density presets, respecting the device's display size and accessibility settings.

### 3. Power menu
A restrained power menu with standard power actions first. Any additional shortcuts must be opt-in, clearly named, and must not weaken lock-screen security or bypass authentication.

### 4. Gestures
Optional navigation and screen-off gestures only where supported by the device and framework. Each gesture needs:
- An explicit enable/disable switch.
- A conflict-free default.
- A way to disable it without relying on the gesture itself.
- No hidden collection of user activity.

### 5. Visual polish
- Consistent SystemUI spacing and iconography.
- Subtle, short animations with no reduction in accessibility.
- Lock-screen and notification styling that remains legible in light and dark themes.

## Implementation strategy

The first implementation should be deliberately small:

1. Establish a clean LineageOS baseline for `mojito`.
2. Identify the exact Android 17 source locations for the intended SystemUI and Settings changes.
3. Implement one isolated change at a time, behind a default-safe setting.
4. Build and test after each change; do not stack untested patches.
5. Keep each feature in a separate commit and document its behavior and rollback path.

Potential source areas (to be confirmed against the synced tree):
- `frameworks/base` — framework behavior and SystemUI.
- `packages/apps/Settings` — ROM settings screens.
- `packages/SystemUI` — Quick Settings, status bar, and power menu UI.
- Resource overlays — device- or product-specific visual defaults.

These are candidate locations, not a claim that the current repository already contains the required integration points.

## First milestone

**Milestone 0 — design and source validation**

- [x] Record the product direction and feature boundaries.
- [ ] Verify the device manifest against the exact LineageOS 24.0 platform revision.
- [ ] Obtain a clean, buildable LineageOS baseline.
- [ ] Choose one low-risk SystemUI customization.
- [ ] Add the first implementation and test notes.

## Non-goals for the first release

- Replacing core Android security behavior.
- Adding persistent services solely for cosmetic effects.
- Bundling proprietary Google/Pixel applications or assets.
- Promising battery or performance improvements without measurements.
- Publishing a flashable package before build and device validation.
