# RichardOS branding

## Identity

- **Name:** RichardOS
- **Tagline:** Your Android. Your rules.
- **Mascot / logo direction:** a geometric lion head, front-facing, with a
  distinctive angular mane. The mark should remain recognizable at small
  sizes and work in monochrome.
- **Primary palette:** graphite / near-black with warm gold as the accent.
- **Style:** restrained, technical, confident; avoid photorealism and excessive
  gradients.

## Usage

The lion is the RichardOS project mark. It must be original artwork and must
not reuse LineageOS, Android, Xiaomi, or Pixel logos.

Recommended placements:
- boot animation and boot splash (separate implementation work);
- Settings branding and About screen;
- project website and repository artwork;
- wallpapers and release graphics.

## Build branding

Product-level Android branding lives in `vendor/richardos/config/branding.mk`.
It is intentionally isolated from upstream LineageOS files. The device product
makefile must include it after the platform product configuration. That include
has not yet been applied because the exact synced device-tree makefile and
include order have not been validated.

No boot animation, logo asset, Settings UI branding, or compiled ROM branding
is claimed to exist yet.
