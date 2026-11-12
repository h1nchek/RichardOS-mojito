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
- boot animation and boot splash (separate implementation work).

## Build branding

Product-level Android branding lives in `vendor/richardos/config/branding.mk`.
It is intentionally isolated from upstream LineageOS files. The device product
makefile must include it after the platform product configuration. That include
has not yet been applied because the exact synced device-tree makefile and
include order have not been validated.

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

This installs Nocturne as the framework's default wallpaper resource; it does
not add a multi-wallpaper picker. Eclipse and Aurum remain artwork masters for
a later wallpaper picker integration.

## Integration status

The lion and three wallpaper masters are committed as original RichardOS
branding source assets. Automated default-wallpaper overlay installation is provided, but it has not
been run against a complete Android checkout or verified in a build. Settings
integration, a multi-wallpaper picker, and boot animation branding remain pending.
No compiled ROM branding is claimed yet.
