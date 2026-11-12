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

The SVG asset is now committed, but it is not yet wired into Android resources,
Settings, or the boot animation. No compiled ROM branding is claimed yet.
