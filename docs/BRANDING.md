# RichardOS branding

## Identity

- **Name:** RichardOS
- **Tagline:** Your Android. Your rules.
- **Mascot / logo:** the approved gold geometric lion emblem, stored at
  [`vendor/richardos/branding/richardos-lion.svg`](../vendor/richardos/branding/richardos-lion.svg).
- **Primary palette:** graphite / near-black with warm gold (`#F5BE35`) as
  the accent.
- **Style:** restrained, technical, confident; avoid photorealism and excessive
  gradients.

## Logo asset

The SVG is a transparent-background, 512×512 vector mark. It is intended for
repository artwork and can be adapted for Settings, boot graphics, and
wallpapers. The current SVG is a traced vector version of the approved lion
image; small contour differences from the raster reference may remain.

## Usage

The lion is the RichardOS project mark. It must not be combined with or
presented as an official LineageOS, Android, Xiaomi, or Pixel logo.

Recommended placements:
- Settings branding and About screen;
- project channel and repository artwork;
- wallpapers and release graphics;
- system accent palette and boot animation.

## System-wide identity

The branding layer is kept in RichardOS-owned files rather than editing upstream
LineageOS sources directly:

- `vendor/richardos/config/branding.mk` sets the RichardOS product brand and
  `ro.richardos.*` identity properties while preserving the `lineage_mojito`
  lunch product name and the real Redmi Note 10 model identity.
- `vendor/richardos/overlay/frameworks/base/core/res/res/values/colors.xml`
  supplies warm-gold Material You accent palettes for light and dark themes. The system-branding installer registers `vendor/richardos/overlay` through `PRODUCT_PACKAGE_OVERLAYS` so the SetupWizard and framework resources are actually included in resource merging.
  Neutral surfaces remain Android-controlled; wallpaper-based dynamic color
  selection may still replace the base palette.
- `vendor/richardos/overlay/packages/apps/SetupWizard/res/values/strings.xml` replaces the upstream Lottie welcome animation with an ImageView using the existing approved lion emblem (rendered by `install-system-branding.sh` as `richardos_lion.png`), changes the verified LineageOS 24 welcome title template to `Welcome to RichardOS`, renames the setup app and feature page, and preserves the existing wizard flow. Its `colors.xml` overrides verified SetupWizard accent, footer-button, and finish-arrow resources with RichardOS gold.\n- `vendor/richardos/overlay/packages/apps/Contacts/res/values/colors.xml`
  applies RichardOS gold to the Contacts app's verified primary/action-bar and
  floating-action-button accent resources. Other apps continue to consume the
  shared Android dynamic palette where supported.
- `scripts/install-system-branding.sh` generates a subtle 24-frame lion
  boot animation at 1080×2400, installs the framework palette overlay, and
  registers the product identity and boot animation in the mojito product
  makefile.

The installer checks for the expected mojito product target and requires
`rsvg-convert` or Inkscape, plus `zip`. It appends a RichardOS-owned block to the product
makefile; review that diff before building. The script has not yet been run in a
complete Android checkout, and the animation has not been rendered or tested
on a phone.

## Original wallpaper artwork

Three original portrait wallpaper masters are committed under
`vendor/richardos/branding/wallpapers/`:

- `richardos-nocturne.svg` — graphite night gradient, gold orbit and flowing lines.
- `richardos-eclipse.svg` — dark eclipse with a warm gold rim.
- `richardos-aurum.svg` — angular gold geometry on graphite.

Each master is 1440×3200 SVG source artwork. Render PNG previews with
`bash scripts/render-wallpapers.sh`; the script uses `rsvg-convert` or
Inkscape. Review the rendered images on the target device before shipping them.

Android's framework default wallpaper resource is raster. Use
`scripts/install-wallpaper-overlay.sh /path/to/android/source device/xiaomi/mojito/lineage_mojito.mk`
to render the Nocturne master as a 1440×3200 PNG into the framework resource
overlay and register `vendor/richardos/overlay` in the mojito product makefile.
The script checks that the supplied makefile declares `lineage_mojito` and is
idempotent. Review the resulting PNG and makefile diff before building.

This installs Nocturne as the framework's default wallpaper resource. For the
three-image WallpaperPicker2 collection, use
`scripts/install-wallpaper-picker.sh /path/to/android/source`. That helper
copies the partner APK source into the Android tree, renders all three full-size
PNGs and thumbnails, and adds `RichardOSWallpapers` to the mojito product
packages. WallpaperPicker2 discovers the package through its partner-customization
broadcast receiver and reads the `partner_wallpapers` resource array.

The picker integration is based on the LineageOS 24.0 WallpaperPicker2 legacy
partner-resource contract. It does not replace WallpaperPicker2 or add a
separate wallpaper application.

## Integration status

The lion and three wallpaper masters are committed as original RichardOS
branding source assets. Automated default-wallpaper overlay installation is provided, but it has not
been run against a complete Android checkout or verified in a build. Settings integration, SetupWizard/Contacts resource overlays, Material You palette overlay, boot-animation generator, and WallpaperPicker2 partner APK are source-level additions. None has been compiled or tested on a device.
No compiled ROM branding is claimed yet.
