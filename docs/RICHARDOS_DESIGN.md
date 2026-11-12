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


## RichardOS Hub v1 — agreed product specification

The following decisions are confirmed for the first Hub release:

- **Visual language:** Pixel Settings-inspired layout and interaction patterns, implemented with original RichardOS branding and assets.
- **Monet:** Android dynamic color plus curated RichardOS palettes and manual accent selection where the platform supports it.
- **Root & System:** read-only root-manager information and system diagnostics. Hub does not attempt to hide root, spoof integrity, or bypass application security checks.
- **Initial categories:** Monet & Themes, Status Bar & Quick Settings, Root & System, and Lock Screen.

### Hub home

The home screen contains four clearly named category cards, a short device/build summary, and an optional notice area for actionable system warnings. It should not show alarming warnings for ordinary unlocked-bootloader or rooted configurations; status must be factual and explained.

All controls should use standard Settings patterns: title, concise summary, current value, and a preview when visual output is affected. Include a per-category reset and a global reset with confirmation.

### A. Monet & Themes


**Confirmed palette model: curated palettes + custom color picker**

The Monet experience combines both approaches:

- **Curated palettes:** a small, quality-controlled set of RichardOS palettes with names and preview swatches. Initial candidates: Ocean, Sage, Orchid, Ember, Graphite, and Rose.
- **Custom accent:** a color picker for choosing a preferred accent color, with a preview before applying.
- **Wallpaper colors:** retain Android's wallpaper-derived dynamic colors as the default and allow returning to them at any time.
- **Mode awareness:** palette previews should be shown in both light and dark themes where supported.
- **Contrast and accessibility:** avoid accepting or applying combinations that make text or essential controls unreadable. Prefer platform-generated tonal palettes and contrast-aware resources rather than simply applying one flat color everywhere.

The initial curated palette names are design placeholders; exact seed colors and tonal mappings will be selected during implementation and validated against Android's dynamic-color engine. The custom picker should select a seed/accent color, not promise arbitrary recoloring of every app.

**V1 controls**
- Theme mode: Follow system / Light / Dark (only if not already adequately exposed by Android Settings; otherwise link to the native control).
- Color source: Wallpaper colors / RichardOS palette.
- Curated palette selection with named previews.
- Manual accent color selection, constrained to supported Android theme resources.
- Preview samples for Settings, Quick Settings, and supported lock-screen elements.
- Reset to system dynamic colors.

**Behavior and constraints**
- Wallpaper-derived colors remain the default.
- Manual palette selection must not claim to recolor third-party apps that do not support dynamic color.
- Prefer Android's existing Monet/theme infrastructure over a parallel color engine.
- Do not promise arbitrary saturation controls until confirmed supported by the selected platform branch.

### B. Status Bar & Quick Settings

**V1 candidate controls**
- Clock: show/hide seconds; optional date display if layout space permits.
- Battery: choose among supported icon/percentage presentation modes.
- Non-essential status icons: individually hide only explicitly supported indicators.
- Quick Settings: supported row/column density presets and tile label presentation.
- Preview of the resulting status bar and QS layout.

**Behavior and constraints**
- Preserve emergency, privacy, microphone/camera, location, and other security-critical indicators.
- Avoid controls that can make essential connectivity or system state misleading.
- Do not promise arbitrary clock positioning or custom tile behavior until the target SystemUI implementation is inspected.
- Respect display size, font scaling, orientation, and accessibility settings.

### C. Root & System

This category is informational and diagnostic in v1.

**V1 information**
- Root status: detected / not detected / unable to determine.
- Recognized manager: Magisk, KernelSU, APatch, other, or unknown, only when detection is reliable.
- Android release, RichardOS build identifier, device codename, kernel release.
- SELinux mode.
- Data-encryption status when exposed through reliable platform APIs.
- Bootloader / Verified Boot state where the platform provides trustworthy values.
- A short explanation for each status and its source.

**Behavior and constraints**
- Never present an unavailable value as a definite pass/fail result.
- Do not collect or upload diagnostics automatically.
- Do not attempt root hiding, integrity spoofing, banking-app bypass, or modification of security state.
- Do not add root-management controls to Hub v1; manager-specific actions belong to the manager's own application.

### D. Lock Screen

**V1 candidate controls**
- Supported clock style choices.
- Date visibility and time format, where supported.
- Notification privacy choice or a shortcut to the native Android control.
- Battery information visibility where supported.
- Lock-screen shortcut configuration only if the platform exposes a safe, maintainable integration point.
- Preview of supported visual changes.

**Behavior and constraints**
- Keep credential, biometric, and lock-screen security flows unchanged.
- Never expose private notification content against the user's Android privacy setting.
- Do not add shortcuts that bypass authentication.
- Weather is not a v1 requirement; it would need a reliable data source and clear privacy behavior.

### Shared interaction rules

- Every setting has a safe default and a concise explanation.
- Visual settings show a preview before or immediately after applying.
- Changes persist across reboot using platform-supported settings storage.
- Settings that require SystemUI restart or reboot must say so before the user applies them.
- Unsupported options are hidden or clearly marked unavailable; never show non-functional switches.
- Accessibility settings and Android security indicators take precedence over cosmetic customization.

### V1 implementation order

1. Hub entry point, category navigation, preference storage, and reset behavior.
2. Monet palette selection using existing Android dynamic-color infrastructure.
3. Root & System read-only diagnostics.
4. A small set of Status Bar / Quick Settings controls after source-level feasibility review.
5. Lock Screen options after identifying supported SystemUI and framework hooks.

This is a product specification, not an implementation claim. Exact APIs, resource names, and source files must be verified against the selected LineageOS 24.0 checkout before code changes are made.
